import sys

import numpy as np

from utli.dir import local_dir
from botpy import logging
_log = logging.get_logger()

try:
    aka_db = np.load(local_dir + '/data/aka_db.npy', allow_pickle=True)
    level_table = np.load(local_dir + '/data/level_table.npy')
    search_db = np.load(local_dir + '/data/search_db.npy')
    _log.info('Load aka_db, level_table, search_db from ./data')
except FileNotFoundError:
    _log.error('Critical npy files not found, if you start whit frist, plase set "version = 0000000000" in config.cfg.')
    sys.exit(1)
