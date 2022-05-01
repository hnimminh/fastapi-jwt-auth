#!/usr/bin/python3

import traceback
import uvicorn

from config import LISTEN_IPADDR, LISTEN_PORT, LOGLEVEL, API_WORKERS
from utils import logger


if __name__ == '__main__':
    try:
        logger.info('module=auth, space=main, state=starting')
        # HTTP API
        logger.debug(f'module=auth, space=main, action=report, httpapi={LISTEN_IPADDR}:{LISTEN_PORT}')
        uvicorn.run('api:httpapi', host=LISTEN_IPADDR, port=LISTEN_PORT, workers=API_WORKERS, log_level=LOGLEVEL.lower(), access_log=False, )
    except Exception as e:
        logger.error(f'module=auth, space=main, state=error, exception={e}, traceback={traceback.format_exc()}')
    finally:
        logger.critical('module=auth, space=main, state=termimated')

