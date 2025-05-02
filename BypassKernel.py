import ctypes
import psutil
from pymem import Pymem
from pymem.process import module_from_name
from colorama import init, Fore, Style

# 初始化并设置自动重置
init(autoreset=True)

def suspend_threads(pid):
    """挂起进程所有线程（参考Windows API实现）"""

def replace_win32_in_memory(process_name, old_str="Win32", new_str="iOS"):
    try:
        # 1. 连接到进程并挂起线程
        pm = Pymem(process_name)
        suspend_threads(pm.process_id)  # 确保进程冻结

        # 2. 扫描内存区域
        main_module = module_from_name(pm.process_handle, process_name)
        start_addr = main_module.lpBaseOfDll
        end_addr = start_addr + main_module.SizeOfImage  # 限定主模块范围

        # 3. 内存搜索与替换（支持多编码）
        pattern = old_str.encode('utf-8')
        replacement = new_str.ljust(len(old_str), '\x00').encode('utf-8')

        current_addr = start_addr
        while current_addr < end_addr:
            try:
                # 按页读取内存（提升效率）
                chunk = pm.read_bytes(current_addr, 4096)
                offset = 0
                while True:
                    pos = chunk.find(pattern, offset)
                    if pos == -1:
                        break
                    target_addr = current_addr + pos
                    # 写入替换内容（长度对齐）
                    pm.write_bytes(target_addr, replacement, len(replacement))
                    print(Fore.GREEN + f"替换成功：地址 {hex(target_addr)}",end='\r')
                    offset = pos + len(pattern)
                current_addr += 4096
            except Exception as e:
                current_addr += 4096  # 跳过不可读区域

    except Exception as e:
        print(Fore.RED + f"错误：{str(e)}",end='\r')
    finally:
        # 可选：恢复线程（根据需求决定是否恢复）
        # resume_threads(pm.process_id)
        pass

if __name__ == "__main__":
    replace_win32_in_memory("Minecraft.Windows.exe")