from flask import Blueprint, render_template, json, current_app
import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import cx_Oracle

from services.db_service import get_oracle_connection
from services.air_service import (
    get_seoul_temp_hub,
    get_seoul_air_quality,
    get_past_air_data
)



bp = Blueprint('main', __name__, url_prefix='/')

def get_all_history(districts):
    # 1. 오라클 연결
    conn = get_oracle_connection()
    cur = conn.cursor()

    # 2. 마지막 업데이트 시간 확인 (오라클 문법: SYSDATE 활용 가능하지만 파이썬에서 계산)
    cur.execute("SELECT * FROM (SELECT TO_CHAR(LAST_UPDATE, 'YYYY-MM-DD HH24:MI:SS') FROM AIR_HISTORY ORDER BY LAST_UPDATE DESC) WHERE ROWNUM = 1")
    row = cur.fetchone()

    now = datetime.datetime.now()
    need_update = True

    if row:
        last_update = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        if (now - last_update).total_seconds() < 900:
            need_update = False

    if need_update:
        all_gu_air, _, _ = get_seoul_air_quality()
        temp_val, _ = get_seoul_temp_hub()

        if temp_val != -999.0:
            cur.execute("MERGE INTO WEATHER_CACHE USING DUAL ON (ID = 1) "
                        "WHEN MATCHED THEN UPDATE SET LAST_TEMP = :1 "
                        "WHEN NOT MATCHED THEN INSERT (ID, LAST_TEMP) VALUES (1, :1)", [temp_val])

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(get_past_air_data, districts))

        for gu, result in zip(districts, results):
            pm25_json = json.dumps(result[0])
            pm10_json = json.dumps(result[1])
            curr = all_gu_air.get(gu, {})

            # 오라클 MERGE 문 (Insert or Update를 한 번에)
            sql = """
                MERGE INTO AIR_HISTORY h
                USING DUAL ON (h.GU_NAME = :1)
                WHEN MATCHED THEN
                    UPDATE SET PM10_JSON=:2, PM25_JSON=:3, O3=:4, NO2=:5, SO2=:6, CO=:7, LAST_UPDATE=SYSDATE
                WHEN NOT MATCHED THEN
                    INSERT (GU_NAME, PM10_JSON, PM25_JSON, O3, NO2, SO2, CO, LAST_UPDATE)
                    VALUES (:1, :2, :3, :4, :5, :6, :7, SYSDATE)
            """
            cur.execute(sql,
                        [gu, pm10_json, pm25_json, curr.get('o3'), curr.get('no2'), curr.get('so2'), curr.get('co')])

        conn.commit()

    # 4. 결과 조립 (오라클에서 읽기)
    new_history = {}
    cur.execute("SELECT GU_NAME, PM25_JSON, PM10_JSON, O3, NO2, SO2, CO FROM AIR_HISTORY")
    rows = cur.fetchall()
    for r in rows:
        # 오라클 CLOB 데이터는 r[1].read() 등으로 읽어야 할 수 있으나 cx_Oracle 설정에 따라 자동 변환됨
        new_history[r[0]] = {
            'hists': [json.loads(r[1] if isinstance(r[1], str) else r[1].read()),
                      json.loads(r[2] if isinstance(r[2], str) else r[2].read())],
            'gases': {'o3': r[3], 'no2': r[4], 'so2': r[5], 'co': r[6]}
        }

    cur.execute("SELECT LAST_TEMP FROM WEATHER_CACHE WHERE ID = 1")
    row_temp = cur.fetchone()
    last_db_temp = row_temp[0] if row_temp else 15.0

    conn.close()
    return new_history, last_db_temp


@bp.route('/')
def index():
    # 1. 메인 랜딩 페이지 (index.html) 렌더링
    # 필요하다면 서울 전체 평균 PM10 정도만 가볍게 가져와서 보여줄 수도 있습니다.
    return render_template('index.html')



# --- [1. 사용자가 접속하는 빠른 대시보드 함수] ---
@bp.route('/dashboard')
def dashboard():
    conn = None  # conn을 미리 None으로 초기화
    try:
        # 1. 수동 업데이트 호출 (테스트 기간에는 놔두셔도 되지만, 안정화되면 주석 처리 하세요)
        # update_dashboard_cache()

        # 2. DB 연결
        conn = get_oracle_connection()
        cur = conn.cursor()

        sql = "SELECT JSON_DATA FROM DISK_DASHBOARD_CACHE WHERE CACHE_KEY = 'MAIN_DASHBOARD'"
        cur.execute(sql)
        row = cur.fetchone()

        if row:
            # LOB 객체 읽기 처리
            raw_json = row[0].read() if hasattr(row[0], 'read') else row[0]
            real_data = json.loads(raw_json)

            # 💡 중요: return 하기 전에 여기서 close를 하지 말고 finally에 맡깁니다.
            return render_template('dashboard.html',
                                   data_sets=json.dumps(real_data, ensure_ascii=False),
                                   history_data=json.dumps(real_data.get('history_data', {}), ensure_ascii=False),
                                   history_data_pm25=json.dumps(real_data.get('history_data_pm25', {}),
                                                                ensure_ascii=False))
        else:
            return "데이터를 생성 중입니다. 잠시 후 새로고침 해주세요.", 202

    except Exception as e:
        import traceback
        print(f"❌ 대시보드 화면 렌더링 에러: {e}")
        return f"화면 로딩 중 에러 발생: <pre>{traceback.format_exc()}</pre>", 500

    finally:
        # 3. 연결이 존재하고 열려있을 때만 닫기
        if conn:
            try:
                conn.close()
            except:
                pass


def update_dashboard_cache():
    # 백그라운드 실행 시 current_app을 인식하기 위해 app_context 사용
    with current_app.app_context():
        print("🔄 대시보드 캐시 갱신 시작...")
        districts = ["종로구", "중구", "용산구", "성동구", "광진구", "동대문구", "중랑구", "성북구", "강북구", "도봉구", "노원구", "은평구", "서대문구", "마포구",
                     "양천구", "강서구", "구로구", "금천구", "영등포구", "동작구", "관악구", "서초구", "강남구", "송파구", "강동구"]

        # [체크] Flask 앱 초기화 시 app.model, app.ratio_df 등이 등록되어 있어야 합니다.
        df = getattr(current_app, 'ratio_df', None)
        model = getattr(current_app, 'model', None)
        scaler = getattr(current_app, 'scaler', None)

        if df is None or model is None or scaler is None:
            print(f"❌ [캐시 업데이트 실패] 모델 로드 상태 확인 필요: df={df is None}, model={model is None}, scaler={scaler is None}")
            return

        try:
            # API 데이터 수집
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_temp = executor.submit(get_seoul_temp_hub)
                future_air = executor.submit(get_seoul_air_quality)
                curr_temp, curr_humi = future_temp.result()
                all_gu_air, time_info_api, common_time = future_air.result()

            all_gu_air = all_gu_air or {}
            all_history, db_temp = get_all_history(districts)

            # 저장용 변수들
            total_risk, pm10_data, pm25_data = {}, {}, {}
            o3_data, no2_data, so2_data, co_data = {}, {}, {}, {}
            cluster_data, history_data, history_data_pm25 = {}, {}, {}

            calc_temp = curr_temp if curr_temp != -999.0 else db_temp
            df_indices = [str(idx).strip() for idx in df.index]
            cols = ['AVG_PM10', 'PM10_LAG1', 'PM10_LAG2', 'PM10_LAG3', 'AVG_PM25', 'PM25_LAG1', 'PM25_LAG2',
                    'PM25_LAG3', 'DUST_TEMP_INTERACTION', 'MANU_RATIO', 'TRANS_RATIO', 'HEALTH_RATIO']

            analysis_full = {}

            for gu in districts:
                try:
                    backup = all_history.get(gu, {'hists': [[None] * 3, [None] * 3], 'gases': {}})
                    pm25_hist_raw, pm10_hist_raw = backup['hists']
                    gu_air = all_gu_air.get(gu)

                    if not gu_air:
                        total_risk[gu] = -1
                        cluster_data[gu] = -1
                        continue

                    raw_pm10 = gu_air.get('pm10')
                    raw_pm25 = gu_air.get('pm25')

                    if (raw_pm10 is None and raw_pm25 is None) or (raw_pm10 == 0 and raw_pm25 == 0):
                        total_risk[gu] = -1
                        cluster_data[gu] = -1
                        continue

                    c_pm10 = float(raw_pm10)
                    c_pm25 = float(raw_pm25)

                    # [보정] 과거 데이터가 없으면 현재 수치로 대체
                    pm10_hist = [int(v) if (v is not None) else int(c_pm10) for v in pm10_hist_raw]
                    pm25_hist = [int(v) if (v is not None) else int(c_pm25) for v in pm25_hist_raw]

                    history_data[gu] = pm10_hist
                    history_data_pm25[gu] = pm25_hist

                    #weighted_input_pm10 = (c_pm10 * 0.7) + (pm10_hist[2] * 0.15) + (pm10_hist[1] * 0.1) + (pm10_hist[0] * 0.05)
                    # weighted_input_pm25 = (c_pm25 * 0.7) + (pm25_hist[2] * 0.15) + (pm25_hist[1] * 0.1) + (pm25_hist[0] * 0.05)

                    # 예측 입력 데이터 생성
                    short_gu = gu.replace("구", "").strip()
                    row_data = df.loc[short_gu] if short_gu in df_indices else df.mean()
                    current_pop = row_data.get('TOTAL_POP', 0)

                    input_dict = {
                        'AVG_PM10': c_pm10, 'PM10_LAG1': pm10_hist[2], 'PM10_LAG2': pm10_hist[1],
                        'PM10_LAG3': pm10_hist[0],
                        'AVG_PM25': c_pm25, 'PM25_LAG1': pm25_hist[2], 'PM25_LAG2': pm25_hist[1],
                        'PM25_LAG3': pm25_hist[0],
                        'DUST_TEMP_INTERACTION': c_pm10 * (30 - calc_temp),
                        'MANU_RATIO': row_data.get('MANU_RATIO', 0),
                        'TRANS_RATIO': row_data.get('TRANS_RATIO', 0),
                        'HEALTH_RATIO': row_data.get('HEALTH_RATIO', 0)
                    }

                    # 모델 예측
                    input_df = pd.DataFrame([input_dict])[cols]
                    print("--- [디버깅] 모델 입력 데이터 ---")
                    print(input_df.iloc[0])  # 서버 콘솔에서 학습 데이터와 비교해보세요
                    print("--- [디버깅] 스케일러 적용 후 값 ---")
                    print(scaler.transform(input_df))
                    scaled_input = scaler.transform(input_df)
                    prediction = int(model.predict(scaled_input)[0])

                    total_risk[gu] = prediction
                    cluster_data[gu] = prediction
                    pm10_data[gu] = raw_pm10
                    pm25_data[gu] = raw_pm25
                    o3_data[gu] = gu_air.get('o3')
                    no2_data[gu] = gu_air.get('no2')
                    so2_data[gu] = gu_air.get('so2')
                    co_data[gu] = gu_air.get('co')

                    analysis_full[gu] = {
                        "pm10": raw_pm10,
                        "pm25": raw_pm25,
                        "o3": gu_air.get('o3', '-'),
                        "no2": gu_air.get('no2', '-'),
                        "so2": gu_air.get('so2', '-'),
                        "co": gu_air.get('co', '-'),
                        "manu": round(row_data.get('MANU_RATIO', 0) * 100, 2),
                        "trans": round(row_data.get('TRANS_RATIO', 0) * 100, 2),
                        "health": round(row_data.get('HEALTH_RATIO', 0) * 100, 2),
                        "total_pop": int(current_pop),
                        "risk": prediction,
                        "trend_pm10": pm10_hist + [raw_pm10 if raw_pm10 is not None else 0],
                        "trend_pm25": pm25_hist + [raw_pm25 if raw_pm25 is not None else 0]
                    }

                except Exception as e:
                    print(f"🔥 {gu} 개별 처리 중 에러: {e}")
                    total_risk[gu] = -1

            # 최종 데이터 구조화
            common_time_str = common_time if common_time else datetime.datetime.now().strftime('%Y%m%d%H%M')
            real_data = {
                'total': total_risk, 'pm10': pm10_data, 'pm25': pm25_data,
                'o3': o3_data, 'no2': no2_data, 'so2': so2_data, 'co': co_data,
                'clusters': cluster_data, 'temp': calc_temp,
                'humi': curr_humi if curr_humi != -999.0 else "점검 중",
                'time': common_time_str, 'time_info': time_info_api,
                'history_data': history_data, 'history_data_pm25': history_data_pm25,

                # [이 줄을 추가!]
                'analysis_data': analysis_full
            }

            # [중요] DB 저장 및 커밋
            conn = get_oracle_connection()
            cur = conn.cursor()
            json_str = json.dumps(real_data, ensure_ascii=False)

            sql = """
                            MERGE INTO DISK_DASHBOARD_CACHE d
                            USING DUAL ON (d.CACHE_KEY = 'MAIN_DASHBOARD')
                            WHEN MATCHED THEN 
                                UPDATE SET JSON_DATA = :json_data, LAST_UPDATED = SYSDATE
                            WHEN NOT MATCHED THEN 
                                INSERT (CACHE_KEY, JSON_DATA, LAST_UPDATED) 
                                VALUES ('MAIN_DASHBOARD', :json_data, SYSDATE)
                        """

            # [핵심] JSON 데이터가 클 수 있으므로 cx_Oracle.CLOB 타입을 명시적으로 지정합니다.
            cur.setinputsizes(json_data=cx_Oracle.CLOB)
            cur.execute(sql, json_data=json_str)

            conn.commit()
            conn.close()
            print(f"✅ DB 캐시 업데이트 완료 (데이터 크기: {len(json_str)}자)")

        except Exception as e:
            import traceback
            print(f"❌ 전체 캐시 업데이트 실패: {traceback.format_exc()}")


@bp.route('/comparison')  # URL을 소문자로 맞추는 것이 관례입니다.
def comparison_view():
    districts = [
        "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구",
        "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구",
        "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구",
        "종로구", "중구", "중랑구"
    ]

    conn = None
    try:
        conn = get_oracle_connection()
        cur = conn.cursor()

        # 1. 이미 생성된 대시보드 캐시 데이터를 가져옵니다.
        # 이 데이터 안에는 'analysis_data'라는 이름으로 25개 구의 모든 정보가 구워져 있습니다.
        sql = "SELECT JSON_DATA FROM DISK_DASHBOARD_CACHE WHERE CACHE_KEY = 'MAIN_DASHBOARD'"
        cur.execute(sql)
        row = cur.fetchone()

        if row:
            # LOB 객체 읽기 및 JSON 변환
            raw_json = row[0].read() if hasattr(row[0], 'read') else row[0]
            real_data = json.loads(raw_json)

            # 2. 캐시된 데이터 중 분석/비교용 데이터를 추출
            analysis_data = real_data.get('analysis_data', {})

            return render_template('Comparison_View.html',
                                   districts=districts,
                                   analysis_data=json.dumps(analysis_data, ensure_ascii=False))
        else:
            # 캐시가 없을 경우에만 최소한의 로직으로 빈 값 전송 또는 안내
            return "데이터 준비 중입니다. 잠시 후 새로고침 해주세요.", 202

    except Exception as e:
        print(f"❌ 비교 페이지 렌더링 에러: {e}")
        return "화면 로딩 중 에러 발생", 500

    finally:
        if conn:
            conn.close()

@bp.route('/analysis')
def analysis():
    districts = [
        "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구",
        "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구",
        "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구",
        "종로구", "중구", "중랑구"
    ]

    conn = None
    try:
        conn = get_oracle_connection()
        cur = conn.cursor()

        # 1. dashboard와 동일한 캐시 데이터를 가져옵니다.
        sql = "SELECT JSON_DATA FROM DISK_DASHBOARD_CACHE WHERE CACHE_KEY = 'MAIN_DASHBOARD'"
        cur.execute(sql)
        row = cur.fetchone()

        if row:
            raw_json = row[0].read() if hasattr(row[0], 'read') else row[0]
            real_data = json.loads(raw_json)

            # 2. 미리 구워진 analysis_data만 꺼내서 프론트로 보냅니다.
            analysis_data = real_data.get('analysis_data', {})

            return render_template('analysis.html',
                                   districts=districts,
                                   analysis_data=json.dumps(analysis_data, ensure_ascii=False))
        else:
            return "데이터를 생성 중입니다. 잠시 후 새로고침 해주세요.", 202

    except Exception as e:
        print(f"❌ 분석 페이지 렌더링 에러: {e}")
        return "화면 로딩 중 에러 발생", 500

    finally:
        if conn: conn.close()












