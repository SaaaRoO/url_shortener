

import os
from celery import Celery

# Make sure the settings module is correctly specified
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.settings')

app = Celery('url_shortener')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
