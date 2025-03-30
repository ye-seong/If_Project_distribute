from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB 초기화
db = SQLAlchemy(app)

# 모델 정의
class PlayerJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(80), unique=True, nullable=False)
    job = db.Column(db.String(80), nullable=False)
    team = db.Column(db.String(10), nullable=False)

# 서버 테스트용 API
@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'server connect success!'})

@app.route('/posttest', methods=['POST'])
def post_test():
    data = request.get_json()
    print("server data:", data)
    return jsonify({'status': 'success', 'received': data})

# 새로운 플레이어 입장
@app.route('/register_player', methods=['POST'])
def register_player():
    data = request.get_json()
    player_id = data.get("player_id")

    if not player_id:
        return jsonify({'status': 'fail', 'reason': 'missing player_id'}), 400

    existing = PlayerJob.query.filter_by(player_id=player_id).first()
    if not existing:
        new_entry = PlayerJob(player_id=player_id, job="", team="")
        db.session.add(new_entry)
        db.session.commit()

    return jsonify({'status': 'success'})

# 플레이어 정보 등록/갱신
@app.route('/update_player', methods=['POST'])
def update_player():
    data = request.get_json()
    player_id = data.get("player_id")
    job = data.get("job")
    team = data.get("team")

    if not player_id or not job or not team:
        return jsonify({'status': 'fail', 'reason': 'missing data'}), 400

    existing = PlayerJob.query.filter_by(player_id=player_id).first()
    if existing:
        existing.job = job
        existing.team = team
    else:
        new_entry = PlayerJob(player_id=player_id, job=job, team=team)
        db.session.add(new_entry)

    db.session.commit()
    return jsonify({'status': 'success'})

# 플레이어 전체 정보 조회
@app.route("/get_players", methods=["GET"])
def get_players():
    jobs = PlayerJob.query.all()
    result = [{"player_id": j.player_id, "job": j.job, "team": j.team} for j in jobs]
    return jsonify(result)

# 선택 현황 및 팀별 중복 직업 체크
@app.route('/get_status', methods=['GET'])
def get_status():
    jobs = PlayerJob.query.all()

    team_job_counts = {}
    for j in jobs:
        team = j.team
        job = j.job

        if team not in team_job_counts:
            team_job_counts[team] = {}

        team_job_counts[team][job] = team_job_counts[team].get(job, 0) + 1

    duplicated_jobs_by_team = {
        team: [job for job, count in job_counts.items() if count > 1]
        for team, job_counts in team_job_counts.items()
    }

    selected_count = len(jobs)
    all_selected = selected_count == 6

    return jsonify({
        "selected_count": selected_count,
        "all_selected": all_selected,
        "duplicated_jobs_by_team": duplicated_jobs_by_team
    })

# DB 초기화 (모든 플레이어 정보 삭제)
@app.route('/clear_jobs', methods=['POST'])
def clear_jobs():
    try:
        num_deleted = PlayerJob.query.delete()
        db.session.commit()
        return jsonify({'status': 'success', 'deleted': num_deleted})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'fail', 'reason': str(e)}), 500

# 실행
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)