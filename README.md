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