import mysql.connector
from utli.cfg_read import cfg

from aqua.ongeki.list import *


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
    cursor.execute(f"SELECT artist_name, name, {level[music_level]} FROM ongeki_game_music where id='{music_id}'")
    result = cursor.fetchall()
    cursor.close()
    cnx.close()
    return result

def select_music_mutlist(music_list):
    # 通过music列表和level列表来批量查找歌曲信息,返回字典
    cnx = mysql.connector.connect(
        host = cfg.mysql_host,
        user = cfg.mysql_user,
        password = cfg.mysql_pwd,
        database = cfg.mysql_db,
        port = cfg.mysql_port
    )
    cursor = cnx.cursor()
    if len(music_list) <= 1:
        select_payload = f"({music_list[0]})"
    else:
        select_payload = tuple(music_list)
    cursor.execute(f"SELECT id, name, level0, level1, level2, level3, level4 FROM ongeki_game_music where id IN {select_payload}")
    result = cursor.fetchall()
    back_list = {}
    for x in result:
        back_list.update({str(x[0]): [x[1], {0: x[2], 1: x[3], 2: x[4], 3:x[5], 4: x[6]}]})
    cursor.close()
    cnx.close()
    return back_list