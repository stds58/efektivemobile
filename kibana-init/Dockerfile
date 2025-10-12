FROM alpine:latest

# Устанавливаем curl и jq
RUN apk add --no-cache curl jq

# Копируем скрипт и данные
COPY kibana-import.sh /usr/local/bin/
COPY export.ndjson /tmp/export.ndjson

RUN chmod +x /usr/local/bin/kibana-import.sh

CMD ["/usr/local/bin/kibana-import.sh"]
