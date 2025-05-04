import ctypes
import psutil
from ctypes import wintypes
import sys
import time
from colorama import Fore, init


# 初始化colorama
init(autoreset=True)

# 定义Windows API类型和函数
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# 常量定义
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_VM_OPERATION = 0x0008
MEM_COMMIT = 0x00001000
PAGE_READWRITE = 0x04
PAGE_EXECUTE_READWRITE = 0x40

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", wintypes.LPVOID),
        ("AllocationBase", wintypes.LPVOID),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD)
    ]

# API函数原型声明
VirtualQueryEx = kernel32.VirtualQueryEx
VirtualQueryEx.argtypes = [
    wintypes.HANDLE, wintypes.LPCVOID,
    ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t
]
VirtualQueryEx.restype = ctypes.c_size_t

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [
    wintypes.HANDLE, wintypes.LPCVOID,
    wintypes.LPVOID, ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t)
]
ReadProcessMemory.restype = wintypes.BOOL

WriteProcessMemory = kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = [
    wintypes.HANDLE, wintypes.LPVOID,
    wintypes.LPCVOID, ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t)
]
WriteProcessMemory.restype = wintypes.BOOL

VirtualProtectEx = kernel32.VirtualProtectEx
VirtualProtectEx.argtypes = [
    wintypes.HANDLE, wintypes.LPVOID,
    ctypes.c_size_t, wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD)
]
VirtualProtectEx.restype = wintypes.BOOL

def modify_memory(process_handle, address, old_str, new_str):
    old_bytes = old_str.encode('utf-8')
    new_bytes = new_str.encode('utf-8')
    
    

    # 修改内存保护属性
    old_protect = wintypes.DWORD(0)
    if not VirtualProtectEx(
        process_handle, address, len(old_bytes),
        PAGE_EXECUTE_READWRITE, ctypes.byref(old_protect)
    ):
        return False

    # 写入新字符串
    bytes_written = ctypes.c_size_t(0)
    success = WriteProcessMemory(
        process_handle, address,
        new_bytes, len(new_bytes),
        ctypes.byref(bytes_written)
    )

    # 恢复内存保护属性
    VirtualProtectEx(
        process_handle, address, len(old_bytes),
        old_protect, ctypes.byref(old_protect)
    )

    return success and bytes_written.value == len(new_bytes)

def replace(process_handle, old_str, new_str):
    target_bytes = old_str.encode('utf-8')
    found = False

    mbi = MEMORY_BASIC_INFORMATION()
    address = 0

    while VirtualQueryEx(process_handle, address, ctypes.byref(mbi), ctypes.sizeof(mbi)):
        if (mbi.State == MEM_COMMIT and 
            mbi.Protect & (PAGE_READWRITE | PAGE_EXECUTE_READWRITE) and 
            mbi.RegionSize > 0):
            
            buffer = ctypes.create_string_buffer(mbi.RegionSize)
            bytes_read = ctypes.c_size_t(0)
            
            if ReadProcessMemory(
                process_handle, address,
                buffer, mbi.RegionSize,
                ctypes.byref(bytes_read)
            ):
                start = 0
                while (pos := buffer.raw.find(target_bytes, start)) != -1:
                    found = True
                    target_address = address + pos
                    print(Fore.LIGHTYELLOW_EX + f"找到地址 0x{target_address:X}")
                    if modify_memory(process_handle, target_address, old_str, new_str):
                        print(Fore.LIGHTGREEN_EX + f"修改成功")
                    else:
                        print(Fore.RED + f"错误: {ctypes.get_last_error()}")
                    start = pos + 1
        
        address += mbi.RegionSize

    return found

def triple_verify(process_handle, old_str):  # 完整扫描
    for i in range(3):
        print(Fore.LIGHTBLUE_EX + f"正在验证... ({i+1}/3)")
        if scan_process_memory(process_handle, old_str):
            return False
        time.sleep(0.3)
    return True

def scan_process_memory(process_handle, target_str):  # 扫描内存
    target_bytes = target_str.encode('utf-8')
    mbi = MEMORY_BASIC_INFORMATION()
    address = 0

    while VirtualQueryEx(process_handle, address, ctypes.byref(mbi), ctypes.sizeof(mbi)):
        if (mbi.State == MEM_COMMIT and 
            mbi.Protect & (PAGE_READWRITE | PAGE_EXECUTE_READWRITE) and 
            mbi.RegionSize > 0):
            
            buffer = ctypes.create_string_buffer(mbi.RegionSize)
            bytes_read = ctypes.c_size_t(0)
            
            if ReadProcessMemory(
                process_handle, address,
                buffer, mbi.RegionSize,
                ctypes.byref(bytes_read)
            ):
                if target_bytes in buffer.raw:
                    return True
        
        address += mbi.RegionSize
    return False

def scan(process_name, old_str, new_str):   
    # 获取PID
    pid = None
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            pid = proc.info['pid']
            break
    
    if not pid:
        print(Fore.RED + f"错误：找不到{process_name}进程")
        return

    # 打开进程句柄
    process_handle = kernel32.OpenProcess(
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ |
        PROCESS_VM_WRITE | PROCESS_VM_OPERATION,
        False, pid
    )
    if not process_handle:
        print(Fore.RED + "错误：无法打开进程，请检查运行时权限")
        return

    # 主循环控制
    max_attempts = 15
    clean_counter = 0
    
    try:
        for attempt in range(1, max_attempts+1):
            print(Fore.LIGHTBLUE_EX + f"\n第 {attempt} 次扫描")
            
            # 执行替换操作
            found = replace(process_handle, old_str, new_str)
            
            if found:
                clean_counter = 0
                print(Fore.LIGHTYELLOW_EX + "检测到残留，继续扫描...")
            else:
                clean_counter += 1
                print(Fore.LIGHTGREEN_EX + f"验证替换完整性... ({clean_counter}/3)")
                
                # 触发三次验证
                if clean_counter >= 5:
                    print(Fore.LIGHTBLUE_EX + "\n继续验证...")
                    if triple_verify(process_handle, old_str):
                        print(Fore.LIGHTGREEN_EX + "\n确认替换完整")
                        return
                    else:
                        clean_counter = 0
                        print(Fore.LIGHTYELLOW_EX + "发现残留，重新修改...")
            
            time.sleep(0.5)  # 降低扫描频率

        print(Fore.RED + "\n替换进程超时！")
    
    finally:
        kernel32.CloseHandle(process_handle)

if __name__ == "__main__":
    scan('Minecraft.Windows.exe', 'Win32', 'IOS')
