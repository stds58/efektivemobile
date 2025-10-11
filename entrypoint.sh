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
from app.utils.importer_data import seed_all
from app.core.config import settings
if settings.ENVIRONMENT == 'development':
    asyncio.run(seed_all())
"
fi

# Запускаем приложение
exec "$@"
#tail -f /dev/null