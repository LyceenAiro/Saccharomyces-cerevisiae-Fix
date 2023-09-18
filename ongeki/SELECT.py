import mysql.connector
import math
from utli.cfg_read import cfg

from .cul import *

from botpy import logging
_log = logging.get_logger()

level = {0: "level0", 1: "level1", 2: "level2", 3: "level3", 10: "level4"}
level_name = {0: "BASIC", 1: "ADVANCED", 2: "EXPERT", 3: "MASTER", 10: "LUNATIC"}
# battle_name = {0: "NOFILE", 1: "ADVANCED", 2: "EXPERT", 3: "MASTER", 10: "LUNATIC"}

def bind_id(qq_id, aime):
    # 绑定用户
    # 防止注入
    _log.info(f"\t[SELECT] 执行绑定aimeID")
    if not aime.isdigit():
        return "AimeID错误"
    # 连接数据库
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


def get_ongeki_pr(qq_id):
    # 最近一次的游玩记录
    # 连接数据库 
    _log.info(f"[SELECT] 正在查询最近游玩记录")
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
    if not AimeID:
        cursor.close()
        cnx.close()
        return "未绑定AimeID"
    AimeID = AimeID[0][0]
    cursor.execute(f"SELECT id FROM sega_card where ext_id='{AimeID}'")
    user = cursor.fetchall()
    user = user[0][0]
    cursor.execute(f"SELECT id FROM ongeki_user_data where aime_card_id='{user}'")
    user_id = cursor.fetchall()
    user_id = user_id[0][0]
    # [1] -> 0 ~ 4  MAP
    # [2] -> 5 ~ 7  RANK
    # [3] -> 8 ~ 13 Note
    cursor.execute(f"SELECT tech_score, battle_score, music_id, level, user_play_date, \
                is_all_break, is_full_combo, is_full_bell, \
                judge_critical_break, judge_break, judge_hit, judge_miss, max_combo, bell_count \
                FROM ongeki_user_playlog where user_id='{user_id}' ORDER BY id DESC LIMIT 1")
    cur = cursor.fetchall()
    full_combo = ""
    full_bell = ""
    if cur[0][5] == 1:
        full_combo = "AB"
    elif cur[0][6] == 1:
        full_combo = "FC"
    if cur[0][7] == 1:
        full_bell = "FB"
    music_id = cur[0][2]
    music_level = cur[0][3]
    cursor.execute(f"SELECT artist_name, name, {level[music_level]} FROM ongeki_game_music where id='{music_id}'")
    music_list = cursor.fetchall()
    cursor.close()
    cnx.close()
    difficulty = float(music_list[0][2].replace(',', '.'))
    rt_name, rt_score = get_rating(cur[0][0], difficulty)
    back = f"{music_list[0][0]}  -  {music_list[0][1]}\n" + \
        "—————————————————\n" + \
        f"Difficulty\t\t{level_name[music_level]} | {difficulty}\n" + \
        f"Score(BS)\t\t{cur[0][0]}({cur[0][1]})\n" + \
        f"Rank\t\t{rt_name} | {full_combo}{full_bell} | {rt_score}\n" + \
        "—————————————————\n" + \
        f"C.BREAK\t{str(cur[0][8]).ljust(6,' ')}\tBREAK\t{str(cur[0][9]).ljust(6,' ')}\n" + \
        f"HIT\t\t{str(cur[0][10]).ljust(6,' ')}\tMISS\t{str(cur[0][11]).ljust(6,' ')}\n" + \
        f"BELLt\t{str(cur[0][13]).ljust(6,' ')}\tCOMBO\t{str(cur[0][12]).ljust(6,' ')}\n" + \
        "—————————————————\n" + \
        f"{cur[0][4].split('.')[0]}\n"
    _log.info(f"[SELECT] 最近游玩记录查询完毕")
    return back

def unbind_id(qq_id):
    # 解绑用户
    # 连接数据库
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
    

    
def get_ongeki_user(qq_id):
    # 查询用户数据
    # 连接数据库
    _log.info(f"[SELECT] 正在查询用户数据")
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
    if not AimeID:
        cursor.close()
        cnx.close()
        return "未绑定AimeID"
    AimeID = AimeID[0][0]
    cursor.execute(f"SELECT id FROM sega_card where ext_id='{AimeID}'")
    user = cursor.fetchall()
    user = user[0][0]
    cursor.execute(f"SELECT user_name, play_count, level, player_rating, highest_rating, battle_point, last_play_date  FROM ongeki_user_data where aime_card_id='{user}'")
    cur = cursor.fetchall()
    cursor.close()
    cnx.close()
    back = "———————————————\n" + \
        f"Aime ID\t\t{AimeID}\n" + \
        f"Name\t\t{cur[0][0]}\n" + \
        f"Play Count\t{cur[0][1]}\n" + \
        f"Level\t\tlv.{cur[0][2]}\n" + \
        f"Rating\t\t{int(cur[0][3])/100}(Max {int(cur[0][4])/100})\n" + \
        f"Battle Point\t{cur[0][5]}\n" + \
        f"Last Play\t\t{cur[0][6].split()[0]}\n" + \
        "———————————————"
    _log.info(f"[SELECT] 用户数据查询完毕")
    return back

def get_ongeki_b30(qq_id):
    # 获取b30数据
    # 连接数据库
    _log.info(f"[SELECT] 正在生成b30数据")
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
    if not AimeID:
        cursor.close()
        cnx.close()
        return "未绑定AimeID"
    AimeID = AimeID[0][0]
    _log.info(f"[SELECT] (0/3)正在查询数据")
    cursor.execute(f"SELECT id FROM sega_card where ext_id='{AimeID}'")
    user = cursor.fetchall()
    user = user[0][0]
    cursor.execute(f"SELECT id FROM ongeki_user_data where aime_card_id='{user}'")
    user_id = cursor.fetchall()                             
    user_id = user_id[0][0]
    cursor.execute(f"SELECT tech_score_max, music_id, level FROM ongeki_user_music_detail where user_id='{user_id}'")
    cur = cursor.fetchall()
    _log.info(f"[SELECT] (1/3)必要数据计算中")
    Songlist = []
    for cur_f in cur:
        music_level = cur_f[2]
        cursor.execute(f"SELECT name, {level[music_level]} FROM ongeki_game_music where id='{cur_f[1]}'")
        music_list = cursor.fetchall()
        difficulty = float(music_list[0][1].replace(',', '.'))
        name = f"{music_list[0][0]}[{level_name[music_level]}]"
        rating = get_rating(cur_f[0], difficulty)
        Songlist.append([name, rating[0]])
    cursor.close()
    cnx.close()
    _log.info(f"[SELECT] (2/3)数据正在打包")
    out_b30 = []
    for num, (name, rating) in enumerate(Songlist, start=0):
        if num < 30:
            out_b30.append([name, rating])
            out_b30 = sorted(out_b30, key=lambda x: x[1])
        else:
            if rating > out_b30[0][1]:
                del out_b30[0]
                out_b30.append([name, rating])
                out_b30 = sorted(out_b30, key=lambda x: x[1])
    _log.info(f"[SELECT] (3/3)打包完成，正在输出")
    back = "———————————————————————————————\nBEST 30\nBP—Rating—Song———————————————————————\n"
    for for_round, (name, rating) in enumerate(out_b30[::-1], start=1):
        inc = f"{for_round}\t{str(rating).ljust(6,' ')}\t{name}\n"
        back = back + inc
    back = back + "———————————————————————————————\nb45的开发受阻了，数据仅供参考并不可信"
    _log.info(f"[SELECT] b30数据生成完毕")
    return back