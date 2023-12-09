from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import current_app

limiter = Limiter(get_remote_address, app=current_app, default_limits=["200 per day", "50 per hour"])