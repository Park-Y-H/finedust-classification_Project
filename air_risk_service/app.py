from flask import Flask
import joblib
import pandas as pd
import threading
from dotenv import load_dotenv

from views import main_views, auth_views, chatbot_views, mask_views
from views.scheduler import start_scheduler
import os

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

    try:
        app.model = joblib.load('models/rf_model.pkl')
        app.scaler = joblib.load('models/scaler.pkl')

        app.model_cols = [
            'AVG_PM10', 'PM10_LAG1', 'PM10_LAG2', 'PM10_LAG3',
            'AVG_PM25', 'PM25_LAG1', 'PM25_LAG2', 'PM25_LAG3',
            'DUST_TEMP_INTERACTION', 'MANU_RATIO', 'TRANS_RATIO', 'HEALTH_RATIO'
        ]

        raw_df = pd.read_csv('data/seoul_ratio.csv')
        raw_df['GU'] = raw_df['GU'].str.replace('구', '', regex=False).str.strip()
        raw_df.set_index('GU', inplace=True)

        denom = raw_df['GRDP'].replace(0, 1)

        processed_df = pd.DataFrame(index=raw_df.index)
        processed_df['MANU_RATIO'] = raw_df['MANU'] / denom
        processed_df['TRANS_RATIO'] = raw_df['TRANS'] / denom
        processed_df['HEALTH_RATIO'] = raw_df['HEALTH'] / denom
        processed_df['TOTAL_POP'] = raw_df['TOTAL_POP']

        app.ratio_df = processed_df.round(4)

        print("✅ 서버 데이터 및 모델 로드 완료!")

    except Exception as e:
        print(f"❌ 초기화 중 오류 발생: {e}")

    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(chatbot_views.bp)
    app.register_blueprint(mask_views.bp)

    threading.Thread(
        target=mask_views.background_mask_calculator,
        daemon=True
    ).start()

    start_scheduler(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)