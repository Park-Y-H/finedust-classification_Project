from flask import Blueprint, render_template, json, session, jsonify, redirect
from services.db_service import get_oracle_connection

import datetime
import time
import requests

bp = Blueprint('mask', __name__, url_prefix='/')



counted_ids = set()
last_save_hour = -1
current_stats = {
    "total_rate": 0, "child_rate": 0, "accum_total": 0, "accum_masked": 0,
    "accum_child_total": 0, "accum_child_masked": 0, "alert": False, "alert_msg": "분석 중..."
}
current_environment = {"dust_level": -1, "dust_label": "데이터 로딩 중...", "user_region": "서울"}




def check_and_save_hourly_history_background():
    global current_stats, counted_ids, last_save_hour
    now = datetime.datetime.now()
    if now.minute == 0 and last_save_hour != now.hour:
        try:
            conn = get_oracle_connection()
            cur = conn.cursor()
            sql = "INSERT INTO MASK_HISTORY_LOG (TOTAL_COUNT, MASKED_COUNT, CHILD_TOTAL, CHILD_MASKED, AVG_RATE) VALUES (:1, :2, :3, :4, :5)"
            cur.execute(sql, (current_stats["accum_total"], current_stats["accum_masked"], current_stats["accum_child_total"], current_stats["accum_child_masked"], current_stats["total_rate"]))
            conn.commit()
            last_save_hour = now.hour
            counted_ids.clear()
            for key in ["accum_total", "accum_masked", "accum_child_total", "accum_child_masked"]: current_stats[key] = 0
            cur.close(); conn.close()
            print(f"✅ [DB 백업] {now.hour}시 데이터 저장 완료")
        except Exception as e:
            print(f"❌ [DB 백업실패]: {e}")

def background_mask_calculator():
    global current_stats, current_environment, counted_ids
    print("🤖 [시스템] 백그라운드 엔진 가동 시작!")
    while True:
        try:
            check_and_save_hourly_history_background()
            res = requests.get("http://localhost:5001/api/predict_mask", timeout=0.5)
            if res.status_code == 200:
                print(f"📡 [디버그] 리눅스 응답: {res.text}")
                data = res.json()
                ids = data.get("id_list", [])
                clss = data.get("cls_list", [])
                for cls, obj_id in zip(clss, ids):
                    if obj_id not in counted_ids:
                        counted_ids.add(obj_id)
                        current_stats["accum_total"] += 1

                        # 전체 마스크 착용 로직
                        if cls in [0, 3]: current_stats["accum_masked"] += 1

                        # 아동 마스크 로직 (3: 아동 착용, 4: 아동 미착용)
                        if cls in [3, 4]:  # 기존 코드의 5는 제외하고 3, 4로 수정 권장
                            current_stats["accum_child_total"] += 1
                            if cls == 3:
                                current_stats["accum_child_masked"] += 1

                            # 💡 [추가] 준수율 계산식
                            if current_stats["accum_child_total"] > 0:
                                current_stats["child_rate"] = int(
                                    (current_stats["accum_child_masked"] / current_stats["accum_child_total"]) * 100)

                    # 전체 착용률 계산
                if current_stats["accum_total"] > 0:
                    current_stats["total_rate"] = int(
                        (current_stats["accum_masked"] / current_stats["accum_total"]) * 100)
                print(f"🔥 [실시간 누적] 총원: {current_stats['accum_total']}명")
        except Exception as e:
            print(f"❌ [스레드 에러]: {e}")
        time.sleep(1.0)

@bp.route('/mask_control')
def mask_control():
    global current_environment
    conn = None
    try:
        conn = get_oracle_connection()
        cur = conn.cursor()
        sql = "SELECT JSON_DATA FROM DISK_DASHBOARD_CACHE WHERE CACHE_KEY = 'MAIN_DASHBOARD'"
        cur.execute(sql)
        row = cur.fetchone()

        real_level = -1
        if row:
            raw_json = row[0].read() if hasattr(row[0], 'read') else row[0]
            data_sets = json.loads(raw_json)
            user_region = session.get('user_region', '중구')
            real_level = data_sets.get('total', {}).get(user_region, 4)

        current_environment["dust_level"] = real_level
        current_environment["dust_label"] = get_risk_label(real_level)
        current_environment["user_region"] = session.get('user_region', '중구')

    except Exception as e:
        print(f"❌ 관제 페이지 데이터 연동 에러: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('ai_mask_control.html')


@bp.route('/video_feed')
def video_feed():
    return redirect("http://localhost:5001/video_feed")


@bp.route('/get_mask_stats')
def get_mask_stats():
    user_region = session.get('user_region', '중구')
    global current_stats, current_environment

    response_data = {
        "total_rate": current_stats["total_rate"],
        "child_rate": current_stats["child_rate"],
        "accum_total": current_stats["accum_total"],
        "accum_masked": current_stats["accum_masked"],
        "accum_child_total": current_stats["accum_child_total"],
        "accum_child_masked": current_stats["accum_child_masked"],
        "alert": current_stats.get("alert", True),
        "alert_msg": current_stats.get("alert_msg", "분석 중..."),
        "dust_level": current_environment["dust_level"],
        "dust_label": current_environment["dust_label"],
        "user_region": user_region
    }
    return jsonify(response_data)


def get_risk_label(level):
    labels = {
        5: "매우나쁨", 3: "나쁨", 4: "보통", 2: "보통", 0: "안전", 1: "안전", -1: "분석 중..."
    }
    return labels.get(level, "분석 중...")



