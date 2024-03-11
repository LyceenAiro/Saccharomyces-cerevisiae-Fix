import mysql.connector
from utli.cfg_read import cfg

from botpy import logging
from aqua.ongeki.list import *
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