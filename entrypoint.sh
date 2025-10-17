#!/bin/sh
# entrypoint.sh

# Выполняем миграции
alembic upgrade head

if [ "$ENVIRONMENT" = "development" ]; then
    python -c "
import asyncio
import os
import sys
sys.path.append('/opt/backend')
import logging
import structlog
from app.core.structlog_configure import configure_logging
from app.utils.importer_data import seed_all
from app.core.config import settings

configure_logging()
logger = structlog.get_logger()


asyncio.run(seed_all())
"
fi

# Запускаем приложение
exec "$@"
#tail -f /dev/null