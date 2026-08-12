from flask import Blueprint, render_template, session, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from services.db_service import get_oracle_connection

import threading
import cx_Oracle
import smtplib
from email.mime.text import MIMEText
import random
import os


bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route('/signup')
def signup(): return render_template('signup.html')


@bp.route('/find_account')
def find_account(): return render_template('find_account.html')

@bp.route('/login')
def login(): return render_template('login.html')

@bp.route('/signup_process', methods=['POST'])
def signup_process():
    data = request.get_json()
    name = data.get('name')
    user_id = data.get('user_id')
    email = data.get('email')
    raw_password = data.get('password')
    region = data.get('region')

    hashed_password = generate_password_hash(raw_password)

    conn = None
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()

        # [중요] 오라클 USERS 테이블 컬럼명에 맞춰 INSERT 문 작성
        # 테이블 구조 예시: NAME, USER_ID, EMAIL, PASSWORD, REGION
        sql = "INSERT INTO USERS (NAME, USER_ID, EMAIL, PASSWORD, REGION) VALUES (:1, :2, :3, :4, :5)"
        cursor.execute(sql, [name, user_id, email, hashed_password, region])

        conn.commit()  # DB 반영

        session['user_id'] = user_id
        session['user_name'] = name
        session['user_region'] = region.strip() if region else ""

        return jsonify({"success": True})

    except cx_Oracle.IntegrityError:
        return jsonify({"success": False, "message": "이미 존재하는 아이디입니다."})
    except Exception as e:
        print(f"❌ 회원가입 DB 에러: {e}")
        return jsonify({"success": False, "message": str(e)})
    finally:
        if conn: conn.close()


@bp.route('/login_process', methods=['POST'])
def login_process():
    data = request.get_json()
    user_id = data.get('user_id')
    user_pw = data.get('password')

    conn = None
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()

        # 아이디와 비번이 맞는지 확인(SELECT)하는 SQL 문입니다.
        sql = "SELECT NAME, REGION, PASSWORD FROM USERS WHERE USER_ID = :1"
        cursor.execute(sql, [user_id])
        user = cursor.fetchone()

        # [수정] 사용자가 존재하고, 해시된 비밀번호가 일치하는지 확인
        if user and check_password_hash(user[2], user_pw):
            session['user_id'] = user_id
            session['user_name'] = user[0]
            session['user_region'] = user[1].strip() if user[1] else ""
            return jsonify({
                "success": True,
                "user_name": user[0]
            })
        else:
            return jsonify({"success": False, "message": "아이디 또는 비밀번호가 틀립니다."})
    except Exception as e:
        print(f"❌ 로그인 DB 에러: {e}")
        return jsonify({"success": False, "message": str(e)})
    finally:
        if conn: conn.close()

@bp.route('/logout')
def logout():
    # 세션의 모든 데이터 삭제 (user_id, user_name 등)
    session.clear()
    # 혹은 특정 데이터만 삭제: session.pop('user_id', None)

    # 팝업을 띄우고 메인으로 보내는 방식
    return "<script>alert('로그아웃 되었습니다.'); location.href='/';</script>"


@bp.route('/mypage')
def mypage():
    if 'user_id' not in session:
        return "<script>alert('로그인이 필요합니다.'); location.href='/login';</script>"

    conn = get_oracle_connection()
    cursor = conn.cursor()
    # 세션 ID를 이용해 사용자 정보 가져오기
    sql = "SELECT NAME, USER_ID, EMAIL, REGION FROM USERS WHERE USER_ID = :1"
    cursor.execute(sql, [session['user_id']])
    user_info = cursor.fetchone()

    if user_info and user_info[3]:
        session['user_region'] = user_info[3].strip()
    conn.close()

    return render_template('mypage.html', user=user_info)


@bp.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    new_pw = data.get('password')
    new_region = data.get('region')
    user_id = session.get('user_id')

    conn = get_oracle_connection()
    cursor = conn.cursor()

    try:
        # 1. DB에 저장된 현재 암호화된 비밀번호 가져오기
        cursor.execute("SELECT PASSWORD FROM USERS WHERE USER_ID = :1", [user_id])
        row = cursor.fetchone()
        current_hashed_pw = row[0] if row else None

        if new_pw:
            # 2. [수정] 새 비밀번호가 기존 비밀번호와 같은지 '함수'로 체크
            # check_password_hash(해시값, 생비밀번호)
            if current_hashed_pw and check_password_hash(current_hashed_pw, new_pw):
                return jsonify({"success": False, "message": "이전 비밀번호와 동일합니다. 다른 비밀번호를 입력해주세요."})

            # 3. 다를 경우 새 비밀번호를 암호화해서 업데이트
            sql = "UPDATE USERS SET PASSWORD = :1, REGION = :2 WHERE USER_ID = :3"
            hashed_new_pw = generate_password_hash(new_pw)
            cursor.execute(sql, [hashed_new_pw, new_region, user_id])
        else:
            # 비밀번호 입력이 없으면 지역만 업데이트
            sql = "UPDATE USERS SET REGION = :1 WHERE USER_ID = :2"
            cursor.execute(sql, [new_region, user_id])

        conn.commit()
        session['user_region'] = new_region
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        conn.close()




# 임시 저장용 (실제 서비스에서는 Redis나 DB 권장)
auth_codes = {}


@bp.route('/send_auth_email', methods=['POST'])
def send_auth_email():
    data = request.get_json()
    email = data.get('email')
    find_type = data.get('type')  # 'id' 또는 'pw' (프론트에서 보낸 값)
    user_id = data.get('user_id')  # 비밀번호 찾기 시에만 들어옴

    if not email:
        return jsonify({"success": False, "message": "이메일 주소가 없습니다."})

    # --- [수정 구간: DB 존재 여부 체크] ---
    conn = get_oracle_connection()  # 기존에 사용하시던 DB 연결 함수
    cursor = conn.cursor()

    try:
        if find_type == 'id':
            # 아이디 찾기: 이메일만 존재하면 됨
            cursor.execute("SELECT COUNT(*) FROM USERS WHERE EMAIL = :1", [email])
        elif find_type == 'pw':
            # 비밀번호 찾기: 아이디와 이메일이 모두 일치해야 함
            cursor.execute("SELECT COUNT(*) FROM USERS WHERE USER_ID = :1 AND EMAIL = :2", [user_id, email])
        else:
            # 회원가입 등 일반 발송인 경우 (기존 로직 유지)
            exists = 1

        if find_type in ['id', 'pw']:
            exists = cursor.fetchone()[0]

        if exists == 0:
            return jsonify({"success": False, "message": "일치하는 회원 정보가 없습니다."})

    except Exception as e:
        return jsonify({"success": False, "message": f"DB 조회 오류: {str(e)}"})
    finally:
        conn.close()
    # --- [체크 종료] ---

    # 인증번호 생성 및 발송 (기존과 동일)
    code = str(random.randint(100000, 999999))
    auth_codes[email] = code

    # 이메일 발송 함수 분리
    def send_mail_task(to_email, auth_code):
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SENDER_EMAIL = os.getenv("MAIL_SENDER_EMAIL")
        SENDER_PW = os.getenv("MAIL_SENDER_PW")

        content = f"인증번호는 [{auth_code}] 입니다."
        msg = MIMEText(content)
        msg['Subject'] = "[서울시 미세먼지] 인증번호"
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PW)
                server.send_message(msg)
        except Exception as e:
            print(f"백그라운드 메일 발송 에러: {e}")

    # [중요] 별도의 쓰레드에서 발송 시작 (서버는 기다리지 않고 즉시 응답)
    threading.Thread(target=send_mail_task, args=(email, code), daemon=True).start()

    return jsonify({"success": True})  # 즉시 성공 응답을 보냄


@bp.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.get_json()
    email = data.get('email')
    input_code = data.get('code')

    if auth_codes.get(email) == input_code:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "인증번호가 일치하지 않습니다."})


@bp.route('/verify_password', methods=['POST'])
def verify_password():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "로그인이 필요합니다."})

    data = request.get_json()
    input_pw = data.get('password')
    user_id = session.get('user_id')

    conn = get_oracle_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT PASSWORD FROM USERS WHERE USER_ID = :1", [user_id])
        row = cursor.fetchone()

        if row and check_password_hash(row[0], input_pw):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})
    finally:
        conn.close()


# [추가] 실제 아이디 찾기 처리
@bp.route('/find_id_result', methods=['POST'])
def find_id_result():
    data = request.get_json()
    email = data.get('email')

    conn = get_oracle_connection()
    cursor = conn.cursor()
    # 이메일로 가입된 아이디 찾기
    cursor.execute("SELECT USER_ID FROM USERS WHERE EMAIL = :1", [email])
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"success": True, "user_id": row[0]})
    else:
        return jsonify({"success": False, "message": "해당 이메일로 가입된 정보가 없습니다."})


# [추가] 비밀번호 재설정 (비밀번호 찾기 후속 단계)
@bp.route('/reset_password_find', methods=['POST'])
def reset_password_find():
    data = request.get_json()
    user_id = data.get('user_id')
    new_pw = data.get('password')

    hashed_pw = generate_password_hash(new_pw)

    conn = get_oracle_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE USERS SET PASSWORD = :1 WHERE USER_ID = :2", [hashed_pw, user_id])
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        conn.close()