from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

app = Celery('mysite')

app.config_from_object('django.conf:settings')
app.conf.worker_cancel_long_running_tasks_on_connection_loss = True
app.conf.broker_connection_retry_on_startup = False

# app.conf.beat_schedule = {
# 	'get_offer':{
# 		'task': 'main.tasks.c_offer',
# 		'schedule': crontab(minute='*/1'),
# 		'args': (),
#
# 	},
# 	'hourly':{
# 		'task': 'main.tasks.hourly',
# 		'schedule': crontab(hour='*/1'),
# 		'args': (),
#
# 	},
# 	'daily':{
# 		'task': 'main.tasks.daily',
# 		'schedule': crontab(minute=0, hour=0),
# 		'args': (),
#
# 	}
# }

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
	print('Request: {0!r}'.format(self.request))