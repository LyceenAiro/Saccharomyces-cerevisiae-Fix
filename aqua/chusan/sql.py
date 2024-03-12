import mysql.connector
from utli.cfg_read import cfg

from aqua.chusan.list import *


def select_music_list(music_id, music_level):
    # 通过musicID和歌曲难度来查询歌曲信息
    cnx = mysql.connector.connect(
        host = cfg.mysql_host,
        user = cfg.mysql_user,
        password = cfg.mysql_pwd,
        database = cfg.mysql_db,
        port = cfg.mysql_port
    )
    cursor = cnx.cursor()
    cursor.execute(f"SELECT artist_name, name, level, level_decimal FROM chusan_music JOIN chusan_music_level ON chusan_music.music_id=chusan_music_level.music_id WHERE chusan_music_level.music_id={music_id} AND diff={music_level}")
    result = cursor.fetchall()
    cursor.close()
    cnx.close()
    return result