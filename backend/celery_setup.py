from celery import Celery, Task
from celery.schedules import crontab


def init_celery(app):
    # Give background tasks access to Flask's database and templates.
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(app.import_name, task_cls=FlaskTask)
    celery.conf.update(
        broker_url='redis://127.0.0.1:6379/0',
        result_backend='redis://127.0.0.1:6379/1',
        timezone='Asia/Kolkata',
        imports=('tasks',),
        beat_schedule={
            'daily-trek-reminders': {
                'task': 'tasks.send_daily_reminders',
                'schedule': crontab(hour=8, minute=0),
            },
            'monthly-admin-report': {
                'task': 'tasks.send_monthly_report',
                'schedule': crontab(day_of_month=1, hour=9, minute=0),
            },
        },
    )
    celery.set_default()
    return celery
