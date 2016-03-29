# Procfile for app
web: python -u run.py serve
worker: celery worker -A tasks.celery -l INFO
