import os, psutil, time
from botpy import logging
from .cfg_read import cfg
_log = logging.get_logger()

##
## 检查应用是否在线
##
## 在配置文件check_app.ini中
## 使用下面格式配置
##
## app.exe|显示的应用名
## app2.exe|显示的应用名
## 

def check_app_service(app_name):
    try:
        total_memory = 0
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == app_name:
                process = psutil.Process(proc.info['pid'])
                total_memory += process.memory_info().rss
                return [True, total_memory]
    except Exception as error:
        _log.error(error)
    return [False, None]


def check_app_service_all():
    _log.info("[Tools] 正在检查软件运行状态")
    if not os.path.exists("check_app.ini"):
        with open("check_app.ini", "a", encoding='utf-8') as file:
            file.write("noapp|默认\n")
    with open("check_app.ini", 'r', encoding='utf-8') as file:
        app_lines = file.readlines()
        if not app_lines:
            return "没有配置监测的软件"
    return_str = "程序状态\n"
    for app_line in app_lines:
        app_info = app_line.strip().split('|')
        if len(app_info) == 2:
            app_name, app_display_name = app_info
            check_app = check_app_service(app_name)
            status = "Ready" if check_app[0] else "Down"
            if check_app[0]:
                if check_app[1] < 1024:
                    return_mem = f"{check_app[1]}B"
                elif check_app[1] < (1024 ** 2):
                    return_mem = f"{check_app[1]/1024}KB"
                elif check_app[1] < (1024 ** 3):
                    return_mem = f"{check_app[1]/1024/1024:.2f}MB"
                else:
                    return_mem = f"{check_app[1]/1024/1024/1024:.2f}GB"
            else:
                return_mem = ""
            return_str += f"{app_display_name:<14}{status:<8}{return_mem}\n"
        else:
            continue
    return return_str.rstrip("\n")

def check_pc():
    _log.info("[Tools] 正在运行系统自检")
    mem_io = psutil.virtual_memory()
    try:
        net_io = psutil.net_io_counters(pernic=True)[cfg.int_interface]
        send = net_io.bytes_sent
        recv = net_io.bytes_recv
        time.sleep(cfg.int_check_time)
        net_io = psutil.net_io_counters(pernic=True)[cfg.int_interface]
        send = (net_io.bytes_sent - send) * 8 / 1e6 / cfg.int_check_time
        recv = (net_io.bytes_recv - recv) * 8 / 1e6 / cfg.int_check_time
        net_io = True
    except:
        net_io = False
    return_str = "硬件状态\n"
    return_str += f"{'RAM':<10}{mem_io.used/1024/1024/1024:.2f}/{mem_io.total/1024/1024/1024:.2f}GB\n"
    return_str += f"{'CPU':<10}{psutil.cpu_percent(interval=1)} %\n"
    if net_io:
        return_str += f"{'SEN':<10}{send:.1f}/{cfg.int_send} Mbps {send/cfg.int_send:.0f}%\n{'REC':<10}{send:.1f}/{cfg.int_recv} Mbps {recv/cfg.int_recv:.0f}%"
    return return_str