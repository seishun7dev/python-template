import re
import uuid
import queue
import atexit
import logging

from logging.handlers import QueueHandler, QueueListener

from app.configs.context import request_id_ctx


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        return True

class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        patterns = [
            r"Basic [a-zA-Z0-9\+/=]+",
            r"Bearer [a-zA-Z0-9\-._~+/]+",
            r"password=[^&]*",
            r"api_key=[^&]*"
        ]
        
        if isinstance(record.msg, str):
            for pattern in patterns:
                record.msg = re.sub(pattern, "REDACTED", record.msg)
        return True

def configure_logging():
    log_queue = queue.Queue(-1)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - [%(request_id)s] - %(message)s'
    )

    # Stdout handler with filters
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(SensitiveDataFilter())

    # Queue handler setup
    queue_handler = QueueHandler(log_queue)
    queue_handler.addFilter(RequestIdFilter())

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(queue_handler)
    root_logger.setLevel(logging.INFO)

    # Create and start listener
    queue_listener = QueueListener(log_queue, stream_handler)
    queue_listener.start()
    
    # Register cleanup
    atexit.register(queue_listener.stop)

    return queue_listener