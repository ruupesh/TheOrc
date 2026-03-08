import structlog

# Configure structlog for the project
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
    cache_logger_on_first_use=True,
)

# Exported logger for use in other modules
logger = structlog.get_logger()
