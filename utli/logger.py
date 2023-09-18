from botpy import logging
_log = logging.get_logger()

from .dir import local_dir, TEST_MODE

_log.info('TEST_MODE on') if TEST_MODE else None
