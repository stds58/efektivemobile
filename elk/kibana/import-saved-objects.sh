#!/bin/bash

set -e



KIBANA_URL="http://localhost:5601"
IMPORT_FILE="/usr/share/kibana/config/pipeline/fastapi-logs.ndjson"
USERNAME="kibana_system"
PASSWORD="$KIBANA_SYSTEM_PASSWORD"

echo "⏳ Ожидание готовности Kibana..."

# Ждём, пока Kibana ответит
until curl -s --fail "$KIBANA_URL/api/status" > /dev/null; do
  echo "Kibana ещё не готова... ждём 5 секунд"
  sleep 5
done

echo "✅ Kibana готова. Импортируем Saved Objects..."

# Импорт через Kibana Saved Objects API
curl -s -X POST "$KIBANA_URL/api/saved_objects/_import" \
  -H "kbn-xsrf: true" \
  -u "$USERNAME:$PASSWORD" \
  --form file=@"$IMPORT_FILE" \
  --form overwrite=true

echo
echo "✅ Импорт завершён."