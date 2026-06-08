web: cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --no-access-log
worker: cd backend && celery -A app.workers.tasks worker --loglevel=info --concurrency=2
