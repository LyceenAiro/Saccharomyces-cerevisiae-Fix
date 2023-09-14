import mysql.connector
from utli.cfg_read import cfg

from .cul import *

cnx = None
level = {0: "level0", 1: "level1", 2: "level2", 3: "level3", 10: "level4"}
level_name = {0: "BASIC", 1: "ADVANCED", 2: "EXPERT", 3: "MASTER", 10: "LUNATIC"}
battle_name = {0: "BASIC", 1: "ADVANCED", 2: "EXPERT", 3: "MASTER", 10: "LUNATIC"}

def mysql_login():
    global cnx
    if cnx is not None:
        return cnx.cursor()
    # 连接数据库
    cnx = mysql.connector.connect(
        host = cfg.mysql_host,
        user = cfg.mysql_user,
        password = cfg.mysql_pwd,
        database = cfg.mysql_db,
        port = cfg.mysql_port
    )
    return cnx.cursor()



def bind_id(qq_id, aime):
    # 防止注入
    if not aime.isdigit():
        return "AimeID错误"
    # 绑定用户
    cursor = mysql_login()
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


def do_pr(qq_id):
    # 最近一次的游玩记录
    cursor = mysql_login()
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
    cursor.execute(f"SELECT artist_name, name, {level[music_level]},  FROM ongeki_game_music where id='{music_id}'")
    music_list = cursor.fetchall()
    cursor.close()
    cnx.close()
    difficulty = float(music_list[0][2].replace(',', '.'))
    rt_name, rt_score = rating(cur[0][0], difficulty)
    back = f"{music_list[0][0]}  -  {music_list[0][1]}\n" + \
        "—————————————————\n" + \
        f"Difficulty\t\t{level_name[music_level]} | {difficulty}\n" + \
        f"Score(BS)\t\t{cur[0][0]}({cur[0][1]})\n" + \
        f"Rank\t\t{rt_name} | {full_combo}{full_bell} | {rt_score}\n" + \
        "—————————————————\n" + \
        f"C.BREAK\t{cur[0][8]}\tBREAK\t{cur[0][9]}\n" + \
        f"HIT\t\t{cur[0][10]}\tMISS\t{cur[0][11]}\n" + \
        f"BELL\t\t{cur[0][13]}\tCOMBO\t{cur[0][12]}\n" + \
        "—————————————————\n" + \
        f"{cur[0][4].split('.')[0]}\n"
    return back

def unbind_id(qq_id):
    # 解绑用户
    cursor = mysql_login()
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
    

    
def user_pack(qq_id):
    # 查询用户数据
    cursor = mysql_login()
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
    return back