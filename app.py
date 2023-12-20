# non-local packages
import os
import sys
# from traceback import format_exc

# interior packages
from utli.cfg_read import cfg

# exterior packages
from parse.asp import ASPParser
from genre import packet

# qqbot
import botpy,asyncio
from botpy import logging
_log = logging.get_logger()
from botpy.message import Message

# mysql
from ongeki.SELECT import *
import mysql.connector

VERSION = [1, 4, 1]


class MyClient(botpy.Client):
    async def on_ready(self):
        self.load_skin()
        self.initSQL()
        # 初始化bot
        _log.info(f"\t[botpy]「{self.robot.name}」 准备完毕！")
    
    async def on_at_message_create(self, message: Message):
        try:
            await asyncio.wait_for(self.on_at_message_do(message), timeout=30)
        except asyncio.TimeoutError:
            # 处理超时逻辑
            _log.info(f"[Return] 上传文件时超时")
            await message.reply(content="上传文件时超时")

    async def on_at_message_do(self, message: Message):
        userID = message.author.id
        _log.info(f"[Return] 用户[{userID}]操作了bot")
        with open("data/card_db.txt", "r") as file:
            lines = file.readlines()
            updated_lines = [line for line in lines if userID not in line.split(":")[0]]
        # 指令执行
        if message.content.split()[1].startswith("/"):
            # 在线查询
            if "/ping" == message.content.split()[1]:
                _log.info(f"[Return] Ping!!!")
                await message.reply(content=f"{self.robot.name}收到你的消息了")
            
            # sdvx查询
            elif "/sdvx" == message.content.split()[1]:
                # 查询最近游玩歌曲的最佳成绩
                if "pr" == message.content.split()[2]:
                    _log.info(f"[SDVX] 查询最近游玩曲目")
                    if len(lines) == len(updated_lines):
                        await message.reply(content="该账号还未绑定KonamiID")
                        return
                    asp = self.user_login(userID)
                    self.plot_skin.plot_single(sg_index=asp.last_index, _music_map=asp.music_map, profile=asp.profile)
                    await message.reply(file_image=f"{cfg.output}/pr.png")

                # 查询best50
                elif "b50" == message.content.split()[2]:
                    _log.info(f"[SDVX] 查询最佳50首曲目")
                    if len(lines) == len(updated_lines):
                        await message.reply(content="该账号还未绑定KonamiID")
                        return
                    asp = self.user_login(userID)
                    self.plot_skin.plot_b50(_music_map=asp.music_map, profile=asp.profile)
                    await message.reply(file_image=f"{cfg.output}/B50.png")
                
                # 查询点灯信息
                elif "sm" == message.content.split()[2]:
                    _log.info(f"[SDVX] 查询点灯信息")
                    if len(lines) == len(updated_lines):
                        await message.reply(content="该账号还未绑定KonamiID")
                        return
                    try:
                        level = int(message.content.split()[3])
                    except:
                        await message.reply(content="请指定查询等级")
                    if level <= 20 and level >= 1:
                        asp = self.user_login(userID)
                        self.plot_skin.plot_summary(base_lv=level, _music_map=asp.music_map, profile=asp.profile)
                        await message.reply(file_image=f"{cfg.output}/SMplus.png")
                    else:
                        await message.reply(content="查询等级错误，等级应该在1~20之间")
                else:
                    return

            # konamiID
            elif "/konami" == message.content.split()[1]:
                # 绑定B系账户
                if "bind" == message.content.split()[2]:
                    _log.info(f"[Konami] 尝试绑定账户")
                    try:
                        cardID = message.content.split()[3]
                        if len(cardID) != 16:
                            await message.reply(content="绑定失败,KonamiID应该为16位")
                            return
                    except:
                        await message.reply(content="绑定KonamiID指令格式\n/bind [ID]")
                        return
                    with open("data/card_db.txt", "r") as file:
                        for line in file:
                            user_id = line.strip().split(":")[0]
                            if user_id == userID:
                                await message.reply(content="绑定失败,该账户已经绑定了KonamiID")
                                return
                    with open("data/card_db.txt", "a") as file:
                        file.write(f"{userID}:{cardID}\n")
                    await message.reply(content=f"成功绑定了KonamiID号{cardID}")

                # 取消绑定B系账户
                elif "unbind" == message.content.split()[2]:
                    _log.info(f"[Konami] 尝试解绑用户")
                    if len(lines) == len(updated_lines):
                        await message.reply(content="该账号还未绑定ID")
                        return
                    with open("data/card_db.txt", "w") as file:
                        file.writelines(updated_lines)
                    await message.reply(content="解绑成功")
                else:
                    return
            
            # aimeID
            elif "/aime" == message.content.split()[1]:
               # 绑定aimeID
                if "bind" == message.content.split()[2]:
                    await message.reply(content=bind_id(userID, message.content.split()[3]))
                elif "unbind" == message.content.split()[2]:
                    await message.reply(content=unbind_id(userID))
                else:
                    return

            # 音击
            elif "/ongeki" == message.content.split()[1]:
                # 获取用户信息
                if "user" == message.content.split()[2]:
                    await message.reply(content=get_ongeki_user(userID))
                elif "pr" == message.content.split()[2]:
                    await message.reply(content=get_ongeki_pr(userID))
                elif "b30" == message.content.split()[2]:
                    await message.reply(content=get_ongeki_b30(userID))
                else:
                    return

            # 帮助页面
            elif "/help" == message.content.split()[1]:
                helpmsg = ("指令帮助[1-sdvx]\n"
                    "/ping\t\t\t查询运行状态\n"
                    "/sdvx b50\t\t获取b50信息\n"
                    "/sdvx pr\t\t\t最近游玩信息\n"
                    "/sdvx sm\t\t\t17+点灯信息\n"
                    "/konami bind [ID]\t绑定ID\n"
                    "/konami unbind\t解绑ID\n"
                    "/help [page]\t\t帮助\n"
                    "————————————————\n"
                    "声明：该bot代码开源且完全免费！！！\n"
                    "GitHub\nLyceenAiro/Saccharomyces-cerevisiae-Fix")
                if len(message.content.split()) > 2:
                    if "2" == message.content.split()[2]:
                        helpmsg = ("指令帮助[2-ongeki]\n"
                        "/aime bind [ID]\t绑定AimeID\n"
                        "/aime unbind\t\t解绑AimeID\n"
                        "/ongeki user\t\t展示用户信息\n"
                        "/ongeki pr\t\t查询最近一次游玩信息\n"
                        "/ongeki b30\t\t查询最好的30首成绩(beta)\n"
                        "/help [page]\t\t帮助\n"
                        "————————————————\n"
                        "声明：该bot代码开源且完全免费！！！\n"
                        "GitHub\nLyceenAiro/Saccharomyces-cerevisiae-Fix")
                _log.info(f"[Return] 帮助页面")
                await message.reply(content=helpmsg)

            else:
                await message.reply(content="暂时还没有这个指令嗷嗷嗷")

        # 非指令动作
        elif "摸摸" in message.content.split()[1]:
            await message.reply(content="嘿嘿~好舒服uwu")
        elif "最近怎么样" in message.content.split()[1]:
            await message.reply(content="还在想~")
        else:
            await message.reply(content="嗷呜~")

    def load_skin(self):
        # 初始化skin
        try:
            self.plot_skin = packet[cfg.skin_name].main
        except KeyError:
            _log.error('没有查询到你选择的皮肤包，请重新在配置文件中选择.')
            sys.exit(1)
    
    def initSQL(self):
        try:
            cnx = mysql.connector.connect(
                host = cfg.mysql_host,
                user = cfg.mysql_user,
                password = cfg.mysql_pwd,
                database = cfg.mysql_db,
                port = cfg.mysql_port
            )
            cursor = cnx.cursor()
            cursor.execute(f"SHOW TABLES LIKE 'qq_card'")
            result = cursor.fetchone()
            if not result:
                create_table_query = """
                CREATE TABLE qq_card (
                    qqid VARCHAR(20) UNIQUE,
                    aimeid VARCHAR(8) UNIQUE
                )
                """
                cursor.execute(create_table_query)
            cursor.close()
            cnx.close()
        except:
            _log.error("[Error]\taqua数据库连接失败，如果这是你第一次连接数据库，请重启直至连接成功")
    
    def user_login(self, userID):
        # Konami用户数据获取
        with open("data/card_db.txt", "r") as file:
            for line in file:
                user_id, card_number = line.strip().split(":")
                if user_id == userID:
                    found_card = card_number
                    break
        asp = ASPParser(db_dir=cfg.db_dir, map_size=cfg.map_size, card_num=found_card)
        asp.get_akaname()
        asp.get_lv_vf()
        return asp


if __name__ == '__main__':
    if not os.path.exists("data/card_db.txt"):
        with open("data/card_db.txt", "a") as file:
            file.write("1:1\n")
    intents = botpy.Intents(public_guild_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=cfg.appid, token=cfg.token)
    