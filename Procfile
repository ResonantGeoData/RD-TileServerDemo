release: ./manage.py migrate
web: gunicorn --bind 0.0.0.0:$PORT ts_demo.wsgi
worker: REMAP_SIGTERM=SIGQUIT celery --app ts_demo.celery worker --loglevel INFO --without-heartbeat
