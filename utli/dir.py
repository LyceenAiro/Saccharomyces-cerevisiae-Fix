from os import path
import sys

from botpy import logging
_log = logging.get_logger()

# The very initial message
print('More information at https://github.com/LyceenAiro/Saccharomyces-cerevisiae-Fix')

TEST_MODE = 1
# Turn off test mode when packing the program
if TEST_MODE:
    local_dir = '/'.join(path.dirname(path.abspath(__file__)).replace('\\', '/').split('/')[:-1])
    _log.info('TEST_MODE on') if TEST_MODE else None
else:
    local_dir = path.dirname(path.abspath(sys.executable)).replace('\\', '/')