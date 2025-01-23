# Practical_Test

## Alembic commands 
- alembic init alembic
for creating migration script
- alembic revision -m "create tgables" 
running migrations
- alembic upgrade head

## fastapi commands 
starting development server
- fastapi dev main.py

stargin uvicorn server manually
- uvicorn main:app --reload

## minio commands
download minio file.
start minio server
- .\minio server /data

set alias for server
- mc alias set 'myminio' 'http://192.168.1.48:9000' 'minioadmin' 'minioadmin'

## celery commands
start redis server
- redis-server

start worker
- celery -A celery worker --loglevel INFO -P gevent 

start celery beat for recurring task
- Command : celery -A celery beat --loglevel INFO 