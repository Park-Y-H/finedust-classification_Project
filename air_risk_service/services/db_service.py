import os
import cx_Oracle

def get_oracle_connection():
    oracle_user = os.getenv("ORACLE_USER")
    oracle_pwd = os.getenv("ORACLE_PWD")

    if not oracle_user or not oracle_pwd:
        raise RuntimeError("ORACLE_USER 또는 ORACLE_PWD 환경변수가 설정되지 않았습니다.")

    dsn = cx_Oracle.makedsn("localhost", 1521, sid="xe")
    conn = cx_Oracle.connect(
        user=oracle_user,
        password=oracle_pwd,
        dsn=dsn
    )

    def output_type_handler(cursor, name, defaultType, size, precision, scale):
        if defaultType == cx_Oracle.CLOB:
            return cursor.var(cx_Oracle.LONG_STRING, arraysize=cursor.arraysize)

    conn.outputtypehandler = output_type_handler
    return conn