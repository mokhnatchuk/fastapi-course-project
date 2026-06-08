# fastapi-course-project

Проєкт з курсу веб-фреймворків на FastAPI.

## Що потрібно:
- Python версії 3.14
- Менеджер пакетів uv
- Docker та Docker Compose

## Як запустити локально:
1. Встановити залежності командою `uv sync`
2. Налаштувати pre-commit командою `uv run pre-commit install`
3. Перевірити код командою `uv run pre-commit run --all-files`
4. Запустити проєкт командою `uv run fastapi dev main.py`

## Як запустити через Docker:
1. Файл `.env` має мати `DATABASE_URL`
2. Зібрати та запустити контейнер командою `docker compose up --build`

Локальний сервер: http://127.0.0.1:8000
Swagger UI: http://127.0.0.1:8000/docs
