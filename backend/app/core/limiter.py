import os

from slowapi import Limiter
from slowapi.util import get_remote_address

# Disabled automatically when running tests
limiter = Limiter(
    key_func=get_remote_address,
    enabled=os.getenv("TESTING", "false").lower() != "true",
)
