
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
