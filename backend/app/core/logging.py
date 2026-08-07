import json
import logging

SENSITIVE = {
    "authorization",
    "cookie",
    "set-cookie",
    "password",
    "token",
    "api_key",
    "service_role_key",
    "database_url",
    "secret",
}


def redact(value):
    if isinstance(value, dict):
        return {
            key: ("[REDACTED]" if any(word in key.lower() for word in SENSITIVE) else redact(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            redact(
                {
                    "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
                    "level": record.levelname,
                    "service": "socra-api",
                    "message": record.getMessage(),
                    **getattr(record, "structured", {}),
                }
            ),
            default=str,
        )


def configure_logging(settings):
    handler = logging.StreamHandler()
    if settings.log_format == "json":
        handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=settings.log_level, handlers=[handler], force=True)
