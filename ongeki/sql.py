import mysql.connector
from utli.cfg_read import cfg

from botpy import logging
from ongeki.list import *
_log = logging.get_logger()


def bind_id(qq_id, aime):
    # 绑定用户
    _log.info(f"\t[SELECT] 执行绑定aimeID")
    # 防止注入及检查格式
    if not aime.isdigit():
        return "AimeID错误"
    cnx = mysql.connector.connect(
        host = cfg.mysql_host,
        user = cfg.mysql_user,
        password = cfg.mysql_pwd,
        database = cfg.mysql_db,
        port = cfg.mysql_port
    )
    cursor = cnx.cursor()
    cursor.execute(f"SELECT id FROM sega_card where ext_id='{aime}'")
    card_save = cursor.fetchall()
    cursor.execute(f"SELECT aimeid FROM qq_card where qqid='{qq_id}'")
    AimeID = cursor.fetchall()
    cursor.execute(f"SELECT qqid FROM qq_card where aimeid='{aime}'")
    binded = cursor.fetchall()
    if not card_save:
        cursor.close()
        cnx.close()
        return "未找到AimeID"
    else:
        if not AimeID:
            if not binded:
                if len(aime) > 10:
                    return "AimeID错误"
                try:
                    cursor.execute(f"INSERT INTO qq_card (qqid, aimeid) VALUES ('{qq_id}', '{aime}')")
                    cnx.commit()
                    cursor.close()
                    cnx.close()
                    return "绑定成功"
                except:
                    cursor.close()
                    cnx.close()
                    return "绑定失败"
            else:
                cursor.close()
                cnx.close()
                return "AimeID已经被绑定了"
        else:
            cursor.close()
            cnx.close()
            return "已经绑定了AimeID"
        
def get_AimeID(qq_id):
    # 通过QQID获取AimeID
    cnx = mysql.connector.connect(
        host = cfg.mysql_host,
        user = cfg.mysql_user,
        password = cfg.mysql_pwd,
        database = cfg.mysql_db,
        port = cfg.mysql_port
    )
    cursor = cnx.cursor()
    cursor.execute(f"SELECT aimeid FROM qq_card where qqid='{qq_id}'")
    AimeID = cursor.fetchall()
    cursor.close()
    cnx.close()
    if not AimeID:
        return None
    return AimeID[0][0]

def unbind_id(qq_id):
    # 解绑用户
    _log.info(f"\t[SELECT] 执行解绑aimeID")
    cnx = mysql.connector.connect(
        host = cfg.mysql_host,
        user = cfg.mysql_user,
        password = cfg.mysql_pwd,
        database = cfg.mysql_db,
        port = cfg.mysql_port
    )
    cursor = cnx.cursor()
    cursor.execute(f"SELECT qqid FROM qq_card where qqid='{qq_id}'")
    card_save = cursor.fetchall()
    if not card_save:
        cursor.close()
        cnx.close()
        return "还未绑定AimeID"
    cursor.execute(f"DELETE FROM qq_card WHERE qqid = '{qq_id}'")
    cnx.commit()
    cursor.close()
    cnx.close()
    return "解绑成功"

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