import logging
from logging.config import dictConfig

import structlog


def configure_logging(log_level: int = logging.INFO) -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    pre_chain = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(),
                    "foreign_pre_chain": pre_chain,
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                }
            },
            "root": {
                "handlers": ["default"],
                "level": log_level,
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "fastapi": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "sqlalchemy": {"handlers": ["default"], "level": "WARNING", "propagate": False},
                "sqlalchemy.engine": {
                    "handlers": ["default"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "sqlalchemy.pool": {"handlers": ["default"], "level": "WARNING", "propagate": False},
                "alembic": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "py.warnings": {
                    "handlers": ["default"],
                    "level": "WARNING",
                    "propagate": False,
                },
            },
        }
    )

    logging.captureWarnings(True)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            timestamper,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None):
    return structlog.get_logger(name)


configure_logging()
logger = get_logger("app")
