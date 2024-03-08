import requests
from urllib3.exceptions import InsecureRequestWarning

from utli.cfg_read import cfg
from aqua.chusan.list import level_name
from aqua.chusan.cul import get_rating
from aqua.aime.sql import get_AimeID
from aqua.chusan.sql import get_AimeID, select_music_list, select_music_mutlist

from time import time
from botpy import logging
_log = logging.get_logger()

def api_payload(api_name, aimeID):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    response = requests.get(f"{cfg.aqua_api}/game/{api_name}?aimeId={aimeID}", verify=False)
    response.raise_for_status()
    return response.json()

def get_chusan_pr(qq_id):
    # 最近一次的游玩记录
    _log.info(f"[chusan] 正在查询最近游玩记录")
    start = time()
    AimeID = get_AimeID(qq_id)
    if AimeID == None:
        return "未绑定AimeID"
    result = api_payload("chuni/v2/recent", AimeID)["content"]
    clear_song = ""
    full_combo = ""
    if result[0]["isClear"] == 1:
        clear_song = "CL"
    elif result[0]["isFullCombo"] == 1:
        full_combo = "FC"
    if result[0]["isAllJustice"] == 1:
        full_combo = "AJ"
    music_level = result[0]["level"]
    music_list = select_music_list(result[0]["musicId"], music_level)
    difficulty = float(music_list[0][2].replace(',', '.'))
    rt_score, rt_name = get_rating(result[0]["techScore"], difficulty)
    back = f"{music_list[0][0]}  -  {music_list[0][1]}\n" + \
        "—————————————————\n" + \
        f"Difficulty\t{level_name[music_level]} | {difficulty}\n" + \
        f"Score(BS)\t{result[0]['techScore']}({result[0]['battleScore']})\n" + \
        f"Rank\t\t{rt_score} | {clear_song}{full_combo} | {rt_name}\n" + \
        "—————————————————\n" + \
        f"C.JUSTICE\t{str(result[0]['judgeCritical'] + result[0]['judgeHeaven']):<10}JUSTICE\t{str(result[0]['judgeJustice']):<6}\n" + \
        f"ATTACK\t{str(result[0]['judgeAttack']):<10}MISS\t{str(result[0]['judgeGuilty']):<6}\n" + \
        f"COMBO\t{str(result[0]['maxCombo']):<6}\n" + \
        "—————————————————\n" + \
        f"{str(result[0]['userPlayDate']).replace("T", " ")}\n"
    _log.info(f"[ongeki] 最近游玩记录查询完毕，耗时 {(time() - start):.2f} 秒")
    return back
    

    
def get_ongeki_user(qq_id):
    # 查询用户数据
    _log.info(f"[ongeki] 正在查询用户数据")
    start = time()
    AimeID = get_AimeID(qq_id)
    if AimeID == None:
        return "未绑定AimeID"
    result = api_payload("ongeki/profile", AimeID)
    last_play = str(api_payload("ongeki/recent", AimeID)["content"][0]["userPlayDate"]).split('.')[0]
    back = "———————————————\n" + \
        f"Aime ID\t\t{AimeID}\n" + \
        f"Name\t\t{result['userName']}\n" + \
        f"Play Count\t{result['playCount']}\n" + \
        f"Level\t\tlv.{result['level']}\n" + \
        f"Rating\t\t{int(result['playerRating'])/100}(Max {int(result['highestRating'])/100})\n" + \
        f"Battle Point\t{result['battlePoint']}\n" + \
        f"Last Play\t{last_play}\n" + \
        "———————————————"
    _log.info(f"[ongeki] 用户数据查询完毕，耗时 {(time() - start):.2f} 秒")
    return back

def get_ongeki_bp(qq_id):
    # 获取b30数据
    _log.info(f"[ongeki] 正在查询bp数据")
    start = time()
    AimeID = get_AimeID(qq_id)
    if AimeID == None:
        return "未绑定AimeID"
    payload = f"{AimeID}&key=rating_base_best"
    result_b30 = api_payload("ongeki/general", payload)["propertyValue"].split(",")
    payload = f"{AimeID}&key=rating_base_new_best"
    result_b15 = api_payload("ongeki/general", payload)["propertyValue"].split(",")
    payload = f"{AimeID}&key=rating_base_hot_best"
    result_r10 = api_payload("ongeki/general", payload)["propertyValue"].split(",")

    # 获取需要查询的乐曲组
    get_musiclist = []
    for data in result_b30:
        get_data = data.split(":")
        if get_data == []:
            break
        get_musiclist.append(get_data[0])
    for data in result_b15:
        get_data = data.split(":")
        if get_data == []:
            break
        get_musiclist.append(get_data[0])
    for data in result_r10:
        get_data = data.split(":")
        if get_data == []:
            break
        get_musiclist.append(get_data[0])
    get_musiclist = list(set(get_musiclist))
    music_list = select_music_mutlist(get_musiclist)

    # 输出数据组合
    back = "———————————————————————————————\nBEST 30\nBP—Rating—Song———————————————————————\n"
    for round, data in enumerate(result_b30, start=1):
        data = data.split(":")
        if data[0] == "0":
            break
        data[1], data[2] = int(data[1]), int(data[2])
        rt_score, rt_name = get_rating(data[2], float(music_list[data[0]][1][data[1]].replace(',', '.')))
        back += f"{round:<4}{rt_score:<6}{music_list[data[0]][0]} [{level_name[data[1]]}]\n"
        
    back += "———————————————————————————————\nNew BEST 15\nBP—Rating—Song———————————————————————\n"
    for round, data in enumerate(result_b15, start=1):
        data = data.split(":")
        if data[0] == "0":
            break
        data[1], data[2] = int(data[1]), int(data[2])
        rt_score, rt_name = get_rating(data[2], float(music_list[data[0]][1][data[1]].replace(',', '.')))
        back += f"{round:<4}{rt_score:<6}{music_list[data[0]][0]} [{level_name[data[1]]}]\n"

    back += "———————————————————————————————\nRecent 10\nBP—Rating—Song———————————————————————\n"
    for round, data in enumerate(result_r10, start=1):
        data = data.split(":")
        if data[0] == "0":
            break
        data[1], data[2] = int(data[1]), int(data[2])
        rt_score, rt_name = get_rating(data[2], float(music_list[data[0]][1][data[1]].replace(',', '.')))
        back += f"{round:<4}{rt_score:<7}{music_list[data[0]][0]} [{level_name[data[1]]}]\n"
    _log.info(f"[ongeki] bp数据查询完毕，耗时 {(time() - start):.2f} 秒")
    return back