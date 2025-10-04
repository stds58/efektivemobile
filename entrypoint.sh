#!/bin/sh
# entrypoint.sh

# Выполняем миграции
alembic upgrade head

# Запускаем приложение
exec "$@"
