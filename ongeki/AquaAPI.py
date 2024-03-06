import requests
from urllib3.exceptions import InsecureRequestWarning

from utli.cfg_read import cfg
from ongeki.list import level_name
from ongeki.cul import get_rating
from ongeki.sql import get_AimeID, select_music_list

from time import time
from botpy import logging
_log = logging.get_logger()

def api_payload(api_name, aimeID):
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    response = requests.get(f"{cfg.aqua_api}/game/{api_name}?aimeId={aimeID}", verify=False)
    response.raise_for_status()
    return response.json()

def get_ongeki_pr(qq_id):
    # 最近一次的游玩记录
    _log.info(f"[ongeki] 正在查询最近游玩记录")
    start = time()
    AimeID = get_AimeID(qq_id)
    if AimeID == None:
        return "未绑定AimeID"
    result = api_payload("ongeki/recent", AimeID)["content"]
    full_combo = ""
    full_bell = ""
    if result[0]["isAllBreak"] == 1:
        full_combo = "AB"
    elif result[0]["isFullCombo"] == 1:
        full_combo = "FC"
    if result[0]["isFullBell"] == 1:
        full_bell = "FB"
    music_level = result[0]["level"]
    music_list = select_music_list(result[0]["musicId"], music_level)
    difficulty = float(music_list[0][2].replace(',', '.'))
    rt_score, rt_name = get_rating(result[0]["techScore"], difficulty)
    back = f"{music_list[0][0]}  -  {music_list[0][1]}\n" + \
        "—————————————————\n" + \
        f"Difficulty\t{level_name[music_level]} | {difficulty}\n" + \
        f"Score(BS)\t{result[0]['techScore']}({result[0]['battleScore']})\n" + \
        f"Rank\t\t{rt_score} | {full_combo}{full_bell} | {rt_name}\n" + \
        "—————————————————\n" + \
        f"C.BREAK\t{str(result[0]['judgeCriticalBreak']):<10}BREAK\t{str(result[0]['judgeBreak']):<6}\n" + \
        f"HIT\t{str(result[0]['judgeHit']):<10}MISS\t{str(result[0]['judgeMiss']):<6}\n" + \
        f"BELL\t{str(result[0]['bellCount']):<10}COMBO\t{str(result[0]['maxCombo']):<6}\n" + \
        "—————————————————\n" + \
        f"{str(result[0]['userPlayDate']).split('.')[0]}\n"
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

    back = "———————————————————————————————\nBEST 30\nBP—Rating—Song———————————————————————\n"
    _log.info(f"[ongeki] 正在查询b30数据")
    for round, data in enumerate(result_b30, start=1):
        data = data.split(":")
        data[1], data[2] = int(data[1]), int(data[2])
        music_list = select_music_list(data[0], data[1])
        if music_list == []:
            break
        music_list = music_list[0]
        rt_score, rt_name = get_rating(data[2], float(music_list[2].replace(',', '.')))
        back += f"{round:<4}{music_list[1]:<30}\t{level_name[data[1]]}\t{rt_score}\n"
        
    back += "———————————————————————————————\nNew BEST 15\nBP—Rating—Song———————————————————————\n"
    _log.info(f"[ongeki] 正在查询b15数据")
    for round, data in enumerate(result_b15, start=1):
        data = data.split(":")
        data[1], data[2] = int(data[1]), int(data[2])
        music_list = select_music_list(data[0], data[1])
        if music_list == []:
            break
        music_list = music_list[0]
        rt_score, rt_name = get_rating(data[2], float(music_list[2].replace(',', '.')))
        back += f"{round:<4}{music_list[1]:<30}\t{level_name[data[1]]}\t{rt_score}\n"

    back += "———————————————————————————————\nRecent 10\nBP—Rating—Song———————————————————————\n"
    _log.info(f"[ongeki] 正在查询r10数据")
    for round, data in enumerate(result_r10, start=1):
        data = data.split(":")
        data[1], data[2] = int(data[1]), int(data[2])
        music_list = select_music_list(data[0], data[1])
        if music_list == []:
            break
        music_list = music_list[0]
        rt_score, rt_name = get_rating(data[2], float(music_list[2].replace(',', '.')))
        back += f"{round:<4}{music_list[1]:<30}\t{level_name[data[1]]}\t{rt_score}\n"
    _log.info(f"[SELECT] bp数据查询完毕，耗时 {(time() - start):.2f} 秒")
    return back