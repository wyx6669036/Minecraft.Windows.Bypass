import ctypes
import os
import sys
import time
import threading
import BypassKernel as kernel
from colorama import Fore, init

init(autoreset=True)# 初始化colorama

def main_text():# 主标题
    print(Fore.LIGHTBLUE_EX + ' ____            ____')
    print(Fore.LIGHTBLUE_EX + '| __ )   _   _  |  _ \\    __ _   ___   ___')
    print(Fore.LIGHTBLUE_EX + '|  _ \\  | | | | | |_) |  / _` | / __| / __|')
    print(Fore.LIGHTBLUE_EX + '| |_) | | |_| | |  __/  | (_| | \\__ \\ \\__ \\')
    print(Fore.LIGHTBLUE_EX + '|____/   \\__, | |_|      \\__,_| |___/ |___/')
    print(Fore.LIGHTBLUE_EX + '         |___/')
    print(Fore.RED + '\n将在1分钟后自动关闭（按下Ctrl + C强制终止）')
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

def counter():  # 计数器线程
    counter_num = 60
    while counter_num > 0:
        counter_num = counter_num - 1
        os.system('cls')
        main_text()
        print(Fore.YELLOW + ' '*51 + f" 将在（{counter_num}）秒后关闭 ", end="\r")
        time.sleep(1)
    Launcher_pid = os.getpid()  # 获取当前进程ID
    os.kill(Launcher_pid, 9)  # 强制终止当前进程

def main():
    if not admin_check():  # 检查权限
        run_as_admin()
        sys.exit(0)
    else:
        main_text()  # 主标题

        # 创建计数器线程
        counter_thread = threading.Thread(target=counter, daemon=True)
        counter_thread.start()

        # 主线程调用 kernel.replace_win32_in_memory
        while True:
            kernel.replace_win32_in_memory("Minecraft.Windows.exe")  # 替换内容（调用Mincraft.Windows.Bypass.Kernel）
            time.sleep(0.1) # 休眠0.1秒，避免CPU占用过高

if __name__ == "__main__":
    main()