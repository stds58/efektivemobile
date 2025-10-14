ARG ELASTIC_VERSION

# https://www.docker.elastic.co/
FROM docker.elastic.co/kibana/kibana:${ELASTIC_VERSION:-9.1.5}

# Add your kibana plugins setup here
# Example: RUN kibana-plugin install <name|url>


# Копируем конфиг и скрипты
#COPY config/kibana.yml /usr/share/kibana/config/kibana.yml
#COPY pipeline/fastapi-logs.ndjson /usr/share/kibana/config/pipeline/fastapi-logs.ndjson
#COPY import-saved-objects.sh /usr/share/kibana/import-saved-objects.sh

