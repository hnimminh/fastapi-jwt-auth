import sys
import re
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
import jwt
import bcrypt
from contextvars import ContextVar

from config import LOGGOUTPUT, LOGLEVEL, SECRET_KEY, DEFAULT_TOKEN_EXPIRY


_request_uuid_ctx_var: ContextVar[str] = ContextVar('request_uuid', default=None)
def get_request_uuid() -> str:
    return _request_uuid_ctx_var.get()


def getlogger(name):
    _logger = logging.getLogger(name)

    if LOGLEVEL == 'DEBUG':
        _logger.setLevel(logging.DEBUG)
    elif LOGLEVEL == 'WARNING':
        _logger.setLevel(logging.WARNING)
    elif LOGLEVEL == 'ERROR':
        _logger.setLevel(logging.ERROR)
    elif LOGLEVEL == 'CRITICAL':
        _logger.setLevel(logging.CRITICAL)
    else:
        _logger.setLevel(logging.INFO)

    FORMATTER = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    if LOGGOUTPUT in ['CONSOLE', 'ALL']:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(FORMATTER)
        _logger.addHandler(console_handler)
    if LOGGOUTPUT in ['FILE', 'ALL']:
        file_handler = TimedRotatingFileHandler('auth.log', when='midnight')
        file_handler.setFormatter(FORMATTER)
        _logger.addHandler(file_handler)

    # with this pattern, it's rarely necessary to propagate the error up to parent
    _logger.propagate = False
    return _logger

logger = getlogger('auth')


def reqinspect(http_request):
    # inspect the http request
    try:
        return {
            'headers': http_request.headers,
            'method': http_request.method.lower(),
            'path': http_request.url.path,
            'query': http_request.query_params._dict
            }
    except:
        return {}


EMAIL_REGEX = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*_-])[A-Za-z\d!@#$%^&*_-]{8,32}$')

def check_email_format(email):
    # The better way is to send them an email and ask them click a link to verify
    # This only able to verify that the email address is syntactically valid. In this assigment just do this way.
    if (re.match(EMAIL_REGEX, email)):
        return True
    else:
        return False


def check_password_format(password):
    if (re.match(PASSWORD_REGEX, password)):
        return True
    else:
        return False


def get_hashed_password(plain_password):
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt())


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


if not SECRET_KEY:
    logger.critical('module=auth, space=security, error=Please specify SECRET_KEY')
    exit()

def generate_jwt_token(email):
    created = datetime.utcnow()
    expiry =  created + timedelta(seconds=DEFAULT_TOKEN_EXPIRY)
    payload = {"iat": created, "exp": expiry, "email": email}
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def validate_jwt_token(credentials):
    try:
        payload = jwt.decode(credentials, SECRET_KEY, algorithms=['HS256'])
    except:
        payload = None

    return payload
