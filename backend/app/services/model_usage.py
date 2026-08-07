import logging

logger = logging.getLogger(__name__)


async def safely_record(operation, *args, **kwargs):
    try:
        await operation(*args, **kwargs)
    except Exception:
        logger.exception("Model usage persistence failed", extra={"contains_prompt": False})
