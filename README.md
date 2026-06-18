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
```bash
git clone https://github.com/mokhnatchuk/fastapi-course-project.git && \
cd fastapi-course-project && \
cp .env.example .env && \
docker compose up --build
```

Локальний сервер: http://127.0.0.1:8000
Swagger UI: http://127.0.0.1:8000/docs

## Міграції бази даних:

Команда для створення нової міграції:
```bash
docker compose exec web uv run alembic revision --autogenerate -m "опис"
```

Команда для застосування міграції:
```bash
docker compose exec web uv run alembic upgrade head
```

---

Команда щоб зробити юзера адміном:
```bash
docker compose exec db psql -U postgres -d fastapi_db -c "UPDATE users SET role='admin' WHERE email='...';"
```
