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
import logging
import structlog
from structlog.processors import CallsiteParameterAdder, CallsiteParameter
from structlog.contextvars import merge_contextvars


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


def configure_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            merge_contextvars,
            structlog.stdlib.add_log_level,
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
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
