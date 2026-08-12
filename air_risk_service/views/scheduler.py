from apscheduler.schedulers.background import BackgroundScheduler
from views.main_views import update_dashboard_cache


def start_scheduler(app):
    def update_cache_with_context():
        with app.app_context():
            update_dashboard_cache()

    try:
        update_cache_with_context()
        print("✅ 서버 시작 시 대시보드 캐시 1회 업데이트 완료!")
    except Exception as e:
        print(f"❌ 서버 시작 시 캐시 업데이트 실패: {e}")

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=update_cache_with_context,
        trigger="interval",
        minutes=15,
        id="dust_update_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )
    scheduler.start()

    return scheduler

