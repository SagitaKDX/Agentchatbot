import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

window_ms = int(os.getenv('RATE_LIMIT_WINDOW_MS', 900000))
max_requests = int(os.getenv('RATE_LIMIT_MAX_REQUESTS', 100))

limiter = Limiter(
    get_remote_address,
    default_limits=[f"{max_requests} per {window_ms // 60000} minutes"],
    headers_enabled=True,
) 