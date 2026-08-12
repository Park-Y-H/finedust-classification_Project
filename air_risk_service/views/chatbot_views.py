from flask import Blueprint, render_template, json, session, request, jsonify
from services.db_service import get_oracle_connection
import requests
import re
import os

bp = Blueprint('chatbot', __name__, url_prefix='/')

RUNPOD_API_URL = os.getenv("RUNPOD_API_URL")

# views.py 내부에 추가
ANALYSIS_MAP = {
    '5': {"health": "매우 위험", "reason": "대기 정체로 인한 고누적 위험군입니다."},
    '3': {"health": "위험", "reason": "고농도 미세먼지 유입 후 잔류 오염원이 해소되지 않았습니다."},
    '4': {"health": "보통 (변동주의)", "reason": "기상 변동에 따라 오염도가 급변할 수 있습니다."},
    '2': {"health": "보통 (누적관리)", "reason": "제조업 기반으로 인해 국지적 영향이 지속되고 있습니다."},
    '1': {"health": "안전 (양호)", "reason": "대기 확산이 원활하여 오염도가 낮습니다."},
    '0': {"health": "안전 (매우 쾌적)", "reason": "보건 최적 상태를 유지하고 있습니다."},
    '-1': {"health": "점검 중", "reason": "데이터를 확인할 수 없습니다."}
}

def get_risk_label(level):
    labels = {
        5: "매우나쁨", 3: "나쁨", 4: "보통", 2: "보통", 0: "안전", 1: "안전", -1: "분석 중..."
    }
    return labels.get(level, "분석 중...")


@bp.route('/ask_chatbot', methods=['POST'])
def ask_chatbot():
    data = request.get_json()
    user_message = data.get('message', '')

    # [1] 정규식으로 'OO구' 형태를 질문에서 자동으로 추출
    # 질문에 'OO구'가 포함되어 있는지 찾습니다.
    match = re.search(r'([가-힣]+구)', user_message)
    target_gu = match.group(1) if match else session.get('user_region', '중구')

    # [2] DB 데이터 로드 (범용적 접근)
    analysis_context = f"{target_gu}에 대한 분석 데이터를 찾을 수 없습니다."
    try:
        conn = get_oracle_connection()
        cur = conn.cursor()
        cur.execute("SELECT JSON_DATA FROM DISK_DASHBOARD_CACHE WHERE CACHE_KEY = 'MAIN_DASHBOARD'")
        row = cur.fetchone()
        if row:
            raw_json = row[0].read() if hasattr(row[0], 'read') else row[0]
            real_data = json.loads(raw_json)
            analysis_data = real_data.get('analysis_data', {})

            # DB에 있는 데이터라면 무엇이든 매칭 (하드코딩 불필요)
            gu_data = analysis_data.get(target_gu)

            if gu_data:
                pm10 = gu_data.get('pm10', '측정불가')
                risk = gu_data.get('risk', -1)
                risk_label = get_risk_label(risk)
                reason = gu_data.get('reason', "현재 해당 지역의 분석 정보가 없습니다.")
                analysis_context = f"{target_gu}의 현재 미세먼지(PM10) 농도는 {pm10}이며, 통합 상태는 '{risk_label}'입니다. 상세 분석: {reason}"
            else:
                # 관할 구가 아니라고 하지 말고, 데이터 업데이트 중임을 알림
                analysis_context = f"현재 {target_gu}의 미세먼지 정보는 업데이트 중입니다. 잠시 후 다시 확인해 주세요."
        conn.close()
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")

    # [3] 프롬프트 구성 (target_gu 변수만 활용)
    context = f"""
        당신은 친절하고 정중한 미세먼지 박사입니다. 아래 [데이터]만을 사용하여 사용자의 질문에 상세히 답변하세요.
        - 데이터에 있는 수치(농도 등)와 상태를 반드시 문장에 포함하세요.
        - 말투는 따뜻하고 친절하게 작성하십시오.
        - 3문장 이내로 작성하십시요.

        [데이터]
        {analysis_context}
        """

    # [4] 페이로드 설정
    payload = {
        "prompt": f"### Instruction:\n{context}\n질문: {user_message}\n\n### Response:\n",
        "parameters": {
            "max_new_tokens": 80,  # 50은 너무 짧아 문장이 잘릴 수 있음
            "temperature": 0.4,    # 0.4 정도로 올려야 따뜻한 말투가 나옵니다.
            "repetition_penalty": 2.5, # 10.0은 너무 강합니다. 2.5가 문장 완성도가 가장 높습니다.
            "do_sample": True,     # 자연스러운 생성을 위해 True 필수
            "stop": ["###", "\n\n", "서울시 공기청정시스템"]
        }
    }

    try:
        if not RUNPOD_API_URL:
            return jsonify({"response": "챗봇 API 주소가 설정되지 않았습니다."})

        response = requests.post(RUNPOD_API_URL, json=payload, timeout=300)
        if response.status_code != 200:
            return jsonify({"response": "챗봇 엔진 연결이 원활하지 않습니다."})

        result = response.json()
        answer = result.get('answer', "").replace("### Response:", "").strip()

        # 반복 루프 제거 (이미 넣으셨다면 유지)
        answer = re.sub(r'(.{10,})\1+', r'\1', answer)

        # 만약 모델이 "보통인데 좋음"처럼 모순된 말을 하면,
        # 서버에서 농도와 등급이 명시된 앞부분 문장만 잘라내기
        if "." in answer:
            sentences = [s.strip() for s in answer.split('.') if s.strip()]
            if len(sentences) >= 2:
                answer = f"{sentences[0]}. {sentences[1]}."
            elif len(sentences) == 1:
                answer = f"{sentences[0]}."

        return jsonify({"response": answer})
    except Exception:
        return jsonify({"response": "챗봇 서비스가 일시적으로 점검 중입니다."})


@bp.route('/chatbot')
def chatbot():
    # 1. 지역 설정 (관심지역 -> '중구' 순서)
    user_region = session.get('user_region', '중구').strip()
    if not user_region.endswith('구'):
        user_region += '구'

    air_info = None
    conn = None

    try:
        conn = get_oracle_connection()
        cur = conn.cursor()

        # 2. 대시보드 캐시에서 전체 구 데이터 로드
        sql = "SELECT JSON_DATA FROM DISK_DASHBOARD_CACHE WHERE CACHE_KEY = 'MAIN_DASHBOARD'"
        cur.execute(sql)
        row = cur.fetchone()

        if row:
            raw_json = row[0].read() if hasattr(row[0], 'read') else row[0]
            real_data = json.loads(raw_json)

            # 3. 사용자의 지역 정보 추출
            analysis_data = real_data.get('analysis_data', {})
            air_info = analysis_data.get(user_region)

            # 만약 해당 구 데이터가 없으면 다시 '중구' 시도
            if not air_info:
                air_info = analysis_data.get('중구')

    except Exception as e:
        print(f"❌ 챗봇 데이터 매칭 실패: {e}")
    finally:
        if conn: conn.close()

    # 4. air_data를 템플릿으로 넘겨서 사이드바에 즉시 반영
    return render_template('chatbot.html', air_data=air_info)







