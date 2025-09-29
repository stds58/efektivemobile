
**о проекте**

Механизм безопасности аутентификации

Система реализует двухуровневую защиту сессий пользователей:

    Динамическая ротация ключей подписи
        При каждом перезапуске приложения генерируется новый SECRET_KEY
        Все ранее выданные JWT-токены автоматически становятся невалидными
        Гарантирует принудительное завершение всех активных сессий

    Распределенный черный список токенов
        In-memory кэш служит реестром отозванных токенов
        Время жизни записей соответствует сроку действия access-токенов
        Обеспечивает мгновенный logout до естественного истечения срока токена


**cваггер**

http://127.0.0.1:8000/api/docs

**alembic**

    alembic revision --autogenerate -m "Auto-generated migration"
    alembic upgrade head


**pytest**

    pytest tests/ -v

    [tool.pytest.ini_options]
    pythonpath = ["."]
    asyncio_mode = "auto"

**pytest-cov**

    pytest --cov=app tests/ -v

    [tool.coverage.run]
    source = ["app"]
    omit = [
        "app/utils/*",
        "app/main.py",
        "*/__init__.py"
    ]

**Неиспользуемые зависимости (пакеты в venv-е)**

    pip install pip-check-reqs

создать requirements.txt

    uv export --no-hashes > requirements.txt

Найти пакеты, которые установлены, но не импортируются в коде

    pip-extra-reqs app/ tests/

Найти импорты, для которых нет записей в requirements.txt

    pip-missing-reqs app/ tests/

**ruff**

чтобы проверить:

    ruff check .

чтобы проверить и попытаться исправить ошибки: 

    ruff check --fix .

Отформатировать код, чтобы форматирование было в соответствие с ruff:

    ruff format app