import os

# APPLICATION IDENTIFY
_APPLICATION = 'Auth BDC'
_DESCRIPTION = 'Auth - Backend Deverloper Challenge'
_SWVERSION = '0.0.0'

#---------------------------------------------------#
# ENVIRONMENT VARIABLE                              #
#---------------------------------------------------#
# LOGGING
LOGGOUTPUT = os.getenv('LOGGOUTPUT')
if not LOGGOUTPUT:
    LOGGOUTPUT = 'CONSOLE'

LOGLEVEL = os.getenv('LOGLEVEL')
try:
    LOGLEVEL = LOGLEVEL.upper()
    if LOGLEVEL not in ['DEBUG', 'ERROR', 'CRITICAL', 'WARNING']:
        LOGLEVEL = 'INFO'
except:
    LOGLEVEL = 'INFO'

# HTTP API - LISTEN IP ADDRESS
LISTEN_IPADDR = os.getenv('LISTEN_IPADDR')
if LISTEN_IPADDR and LISTEN_IPADDR.lower() == 'local':
    LISTEN_IPADDR = '127.0.0.1'
else:
    LISTEN_IPADDR = '0.0.0.0'

# HTTP API - LISTEN PORT
LISTEN_PORT = os.getenv('LISTEN_PORT')
try:
    LISTEN_PORT = int(LISTEN_PORT)
    if LISTEN_PORT >  65535 or LISTEN_PORT < 1:
        LISTEN_PORT = 80
except:
    LISTEN_PORT = 80

# NUMBER OF API WORKERS
API_WORKERS = os.getenv('API_WORKERS')
try:
    API_WORKERS = int(API_WORKERS)
    if API_WORKERS >  8 or API_WORKERS < 1:
        API_WORKERS = 1
except:
    API_WORKERS = 1

# SECRET KEY FOR JWT
SECRET_KEY = os.getenv('SECRET_KEY')

# DEFAULT EXPIRY TIME (in second) OF JWT_TOKEN, default = 24*3600 = 86400
DEFAULT_TOKEN_EXPIRY = os.getenv('DEFAULT_TOKEN_EXPIRY')
try:
    DEFAULT_TOKEN_EXPIRY = int(DEFAULT_TOKEN_EXPIRY)
    if DEFAULT_TOKEN_EXPIRY > 7*86400 or DEFAULT_TOKEN_EXPIRY < 60:
        DEFAULT_TOKEN_EXPIRY = 600
except:
    DEFAULT_TOKEN_EXPIRY = 600

# MYSQL DATABASES
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DB')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = os.getenv('MYSQL_PORT')
try:
    MYSQL_PORT = int(MYSQL_PORT)
    if MYSQL_PORT >  65535 or MYSQL_PORT < 1:
        MYSQL_PORT = 3306
except:
    MYSQL_PORT = 3306
