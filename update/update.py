from os import path, makedirs, system
from time import sleep

from .db import update_db
from .aka import update_aka
from .img import update_img

from utli.dir import local_dir
from botpy import logging
_log = logging.get_logger()


def update(cfg, game_only: bool = False):
    _log.warning('Since you have updated your game (or simply the maiden run of this application), '
                   'the program is going to generate some relative data.\n'
                   'It may take some time to finish, press enter to continue.')

    if not path.exists(local_dir + '/data/'):
        makedirs(local_dir + '/data/')

    # Set up level_table.npy and aka_db.npy
    update_db(cfg.game_dir, cfg.map_size)
    if path.exists(local_dir + '/data/level_table.npy'):
        _log.info('generate level_table.npy successfully.')
    else:
        _log.error('Fail to generate level_table.npy.')
    if path.exists(local_dir + '/data/search_db.npy'):
        _log.info('generate search_db.npy successfully.')
    else:
        _log.error('Fail to generate search_db.npy.')

    update_aka(cfg.game_dir)
    if path.exists(local_dir + '/data/aka_db.npy'):
        _log.info('generate aka_db.npy successfully.')
    else:
        _log.error('Fail to generate aka_db.npy.')

    if not game_only:
        update_img(cfg.game_dir, cfg.skin_name)
    if path.exists(local_dir + '/img_archive/%s' % cfg.skin_name):
        _log.info('(maybe) generate image archive successfully.')
    else:
        _log.error('Fail to generate image archive.')

    sleep(0.1)
    _log.info('\nUpdate complete. Press enter to continue.')
    system('cls')
