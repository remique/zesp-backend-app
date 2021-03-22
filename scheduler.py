from flask_apscheduler import APScheduler
from database.models import Activity
from database.db import db

scheduler = APScheduler()


# For testing:
# @scheduler.task('interval', id='do_job_1', seconds=5)
@scheduler.task('cron', id='do_job_1', day_of_week='*')
def job1():
    with scheduler.app.app_context():
        all_activities = Activity.query.all()
        for activity in all_activities:
            activity.food_scale = 0
            activity.sleep = 0

            db.session.commit()

        print("Activities cleared!")
