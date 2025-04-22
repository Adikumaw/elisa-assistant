# scheduler_core.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

scheduler = BackgroundScheduler(
    jobstores={"default": SQLAlchemyJobStore(url="sqlite:///reminder_jobs.sqlite")},
    executors={"default": ThreadPoolExecutor(10)},
    timezone="Asia/Kolkata"
)
scheduler.start()
