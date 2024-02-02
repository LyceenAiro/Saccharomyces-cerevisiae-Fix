import subprocess
from botpy import logging
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
        tasklist_output = subprocess.check_output(['tasklist'], shell=True).decode('utf-8', errors='ignore')
        return app_name in tasklist_output
    except Exception as error:
        _log.error(error)
        return False


def check_app_service_all():
    _log.info("[Tools] 正在检查软件运行状态")
    with open("check_app.ini", 'r', encoding='utf-8') as file:
        app_lines = file.readlines()
    return_str = "程序状态\n"
    for app_line in app_lines:
        app_info = app_line.strip().split('|')
        if len(app_info) == 2:
            app_name, app_display_name = app_info
            is_running = check_app_service(app_name)
            status = "Ready" if is_running else "Down"
            return_str += f"{app_display_name:<15}{status}\n"
    return return_str.rstrip("\n")
