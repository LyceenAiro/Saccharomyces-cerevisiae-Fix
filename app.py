# non-local packages
import os
import re
import sys
import time
import urllib.request
from traceback import format_exc

# interior packages
from utli.cfg_read import cfg
from utli.logger import timber

# exterior packages
from parse.asp import ASPParser
from genre import packet

# qqbot
import botpy,asyncio
from botpy import logging
from botpy.message import Message

VERSION = [1, 4, 1]

_log = logging.get_logger()

class MyClient(botpy.Client):
    async def on_ready(self):
        self.load_skin()
        # 初始化bot
        _log.info(f"robot 「{self.robot.name}」 on_ready!")
    
    async def on_at_message_create(self, message: Message):
        try:
            await asyncio.wait_for(self.on_at_message_do(message), timeout=30)
        except asyncio.TimeoutError:
            # 处理超时逻辑
            await message.reply(content="上传文件时超时")

    async def on_at_message_do(self, message: Message):
        userID = message.author.id
        with open("data/card_db.txt", "r") as file:
            lines = file.readlines()
            updated_lines = [line for line in lines if userID not in line.split(":")[0]]
        # 指令执行
        if message.content.split()[1].startswith("/"):
            # 在线查询
            if "/ping" in message.content.split()[1]:
                await message.reply(content=f"{self.robot.name}收到你的消息了")
            
            elif "/sdvx" in message.content.split()[1]:
                # 查询最近游玩歌曲的最佳成绩
                if "pr" in message.content.split()[2]:
                    if len(lines) == len(updated_lines):
                        await message.reply(content="该账号还未绑定KonamiID")
                        return
                    asp = self.user_login(userID)
                    self.plot_skin.plot_single(sg_index=asp.last_index, _music_map=asp.music_map, profile=asp.profile)
                    await message.reply(file_image=f"{cfg.output}/pr.png")

                # 查询best50
                elif "b50" in message.content.split()[2]:
                    if len(lines) == len(updated_lines):
                        await message.reply(content="该账号还未绑定KonamiID")
                        return
                    asp = self.user_login(userID)
                    self.plot_skin.plot_b50(_music_map=asp.music_map, profile=asp.profile)
                    await message.reply(file_image=f"{cfg.output}/B50.png")

            elif "/konami" in message.content.split()[1]:
                # 绑定B系账户
                if "bind" in message.content.split()[2]:
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
                elif "unbind" in message.content.split()[2]:
                    if len(lines) == len(updated_lines):
                        await message.reply(content="该账号还未绑定ID")
                        return
                    with open("data/card_db.txt", "w") as file:
                        file.writelines(updated_lines)
                    await message.reply(content="解绑成功")

            # 帮助页面
            elif "/help" in message.content.split()[1]:
                helpmsg = ("指令帮助\n"
                "/ping\t查询运行状态\n"
                "/sdvx b50\t获取b50信息\n"
                "/sdvx pr\t\t最近游玩信息\n"
                "/konami bind [ID]\t绑定ID\n"
                "/konami unbind\t解绑ID\n"
                "/help\t帮助")
                await message.reply(content=helpmsg)

            else:
                await message.reply(content="暂时还没有这个指令嗷嗷嗷")

        # 非指令动作
        elif "摸摸" in message.content.split()[1]:
            await message.reply(content="好舒服")
        else:
            await message.reply(content="嗷呜")
    
    def load_skin(self):
        # 初始化skin
        try:
            self.plot_skin = packet[cfg.skin_name].main
        except KeyError:
            timber.error('Invalid skin name, please check your configurations.')
            sys.exit(1)
    
    def user_login(self, userID):
        # 用户数据获取
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
    