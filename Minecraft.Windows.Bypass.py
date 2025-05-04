import ctypes
import os
import sys
import time
import psutil
from colorama import Fore, init
import pygetwindow as gw
from pywinauto import findwindows

import BypassKernel as kernel


init(autoreset=True)# 初始化colorama

def main_text():# 主标题
    print(Fore.LIGHTBLUE_EX + ' ____            ____')
    print(Fore.LIGHTBLUE_EX + '| __ )   _   _  |  _ \\    __ _   ___   ___')
    print(Fore.LIGHTBLUE_EX + '|  _ \\  | | | | | |_) |  / _` | / __| / __|')
    print(Fore.LIGHTBLUE_EX + '| |_) | | |_| | |  __/  | (_| | \\__ \\ \\__ \\')
    print(Fore.LIGHTBLUE_EX + '|____/   \\__, | |_|      \\__,_| |___/ |___/')
    print(Fore.LIGHTBLUE_EX + '         |___/')
    print(Fore.LIGHTGREEN_EX + '权限足够！（管理员权限）')
    print(Fore.RESET + '_'*100 + '\n')

def admin_check():# 检查权限
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    # 获取当前脚本的完整路径
    script_path = os.path.abspath(__file__)
    # 请求管理员权限
    params = f'"{script_path}"'
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

def process_check(process_name):  # 检查进程是否运行
    while True:
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] == process_name:
                    print(Fore.LIGHTGREEN_EX + f"找到{process_name}！ ")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass  # 忽略异常进程
        time.sleep(0.1)

def main():
    if not admin_check():  # 检查权限
        run_as_admin()
        sys.exit(0)
    else:
        main_text()  # 主标题
        print(Fore.LIGHTYELLOW_EX + "正在等待Minecraft.Windows.exe进程...")
        process_check('Minecraft.Windows.exe')  # 查找Minecraft.Windows.exe进程
        print(Fore.LIGHTBLUE_EX + "正在修改")
        kernel.scan('Minecraft.Windows.exe', 'Win32', 'IOS')  # 调用扫描和替换逻辑
        print(Fore.LIGHTGREEN_EX + "修改成功")
        for i in ['3','2','1']:
            print(Fore.LIGHTYELLOW_EX + f'替换结束，程序自动退出 （{i}）')
            time.sleep(1)

if __name__ == "__main__":
    main()