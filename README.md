# Minecraft.Windows.Bypass
https://www.bilibili.com/video/BV1h6G8zDEk2 的modpc的自动修改内存  
## 这是干什么的
Chaos发布了他的modpc，但是要手动修改内存中内容为“Win32”的字符串为“IOS”或其他的内容，对于手速慢或者电脑太好的用户可能没那么多时间修改  
于是，这个软件就诞生了  
## 原理
使用pymem模块修改内存  
Mincraft.Windows.Bypass.py其实是个外壳+计数器，真正修改内存的在kernel.py里  
会自动获取管理员权限，可以不用手动授予（最好还是手动以管理员权限运行）  
在执行完修改且进入游戏后，可以手动关闭，一分钟只是针对那些电脑不好的进行的设计，你可以自己下载源代码进行修改
## 已知问题
在修改过一次后，如果再出现新的值为“Win32”的字符串，将无法修改且没有输出  
由于使用while True调用修改，在关闭程序前可能造成游戏的卡顿  
（内存修改部分使用deepseek编写，我也看不太懂）
