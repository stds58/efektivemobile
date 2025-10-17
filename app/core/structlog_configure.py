"""
structlog.stdlib.add_logger_name,
    добавляет поле "logger" с именем логгера
    (например, "__main__" или "myapp.api")
structlog.stdlib.PositionalArgumentsFormatter(),
    обрабатывает логи вида logger.info("Hello %s", "world") - превращает в "Hello world"
structlog.processors.StackInfoRenderer(),
    добавляет стек-трейс при вызове logger.info("msg", stack_info=True)
structlog.processors.format_exc_info,
    если в лог передано исключение (например, logger.error("Oops", exc_info=True)),
    он красиво форматирует traceback
"""
import os
import sys
import requests
import logging
import structlog
from structlog.processors import CallsiteParameterAdder, CallsiteParameter
from structlog.contextvars import merge_contextvars
from app.core.config import settings


def ordered_json_processor(logger, method_name, event_dict):
    """
    Формирует event_dict с фиксированным порядком ключей.
    Сначала системные поля, потом всё остальное.
    """
    # Определяем желаемый порядок "системных" полей
    system_keys = [
        "user_id",
        "ip",
        "method",
        "path",
        "duration_s",
        "status",
        "timestamp",
        "level",
        "logger",
        "event",
        "error",
        "business_element",
        "model_id",
        "data",
        "owner_field",
        "filters",
        "pagination",
        "isolation_level",
        "commit",
        "filename",
        "func_name",
        "lineno",
        "worker_pid",
    ]

    # Создаём упорядоченный словарь
    ordered = {}

    # Сначала добавляем системные ключи (если есть)
    for key in system_keys:
        if key in event_dict:
            ordered[key] = event_dict.pop(key)

    # Затем добавляем всё остальное (в порядке появления или sorted)
    # Здесь просто добавляем остаток — порядок не важен
    ordered.update(event_dict)

    return ordered


def add_worker_pid(logger, method_name, event_dict):
    event_dict["worker_pid"] = os.getpid()
    return event_dict


def logstash_processor(logger, method_name, event_dict):
    if settings.DEBUG:
        try:
            requests.post(
                "http://localhost:8080",
                data=event_dict,
                headers={"Content-Type": "application/json"},
                timeout=2
            )
        except Exception as e:
            print("Logstash error:", e)
    return event_dict


def unify_log_level(logger, method_name, event_dict):
    """
    Унифицирует поле уровня лога в 'level'.
    Поддерживает как 'level', так и 'severity' на входе.
    """
    # Если уже есть 'level' — оставляем
    if "level" in event_dict:
        return event_dict

    # Если есть 'severity' — используем его как 'level'
    if "severity" in event_dict:
        # Приводим к нижнему регистру, как делает structlog по умолчанию
        event_dict["level"] = str(event_dict.pop("severity")).lower()
        return event_dict

    # Если ничего нет — ставим 'info' (или другой уровень по умолчанию)
    event_dict["level"] = "info"
    return event_dict


def configure_logging():
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    structlog.configure(
        processors=[
            merge_contextvars,
            structlog.stdlib.add_log_level,
            unify_log_level,
            CallsiteParameterAdder(
                [
                    CallsiteParameter.FILENAME,
                    CallsiteParameter.FUNC_NAME,
                    CallsiteParameter.LINENO,
                ]
            ),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso"),
            add_worker_pid,  # PID воркера
            structlog.processors.dict_tracebacks,
            ordered_json_processor,
            structlog.processors.JSONRenderer(ensure_ascii=False),
            logstash_processor,

        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
