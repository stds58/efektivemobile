#!/bin/sh
set -e

echo "Waiting for Kibana API to respond..."
while ! curl -sf http://kibana:5601/api/status > /dev/null 2>&1; do
  echo "Kibana not ready... sleeping 5s"
  sleep 5
done

echo "Importing saved objects..."
curl -X POST "http://kibana:5601/api/saved_objects/_import?overwrite=true" \
  -H "kbn-xsrf: true" \
  --form file=@/tmp/export.ndjson

echo "Done."
