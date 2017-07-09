
让MBR直接操作硬盘，对硬盘进行读写操作
柱面，磁道，扇区



# 环境

* ubuntu14

* bochs-2.4.5

ubuntu安装bochs有些问题，自行搜索解决

# 代码编写

代码目录，见code目录文件夹

需要自己修改Makefile,生成的目录自行设定

![](../02_mbr_hd/imgs/code_directory.jpg)

* 通过bximage 来制作硬盘

![](../02_mbr_hd/imgs/bximage.jpg)

在配置bochs文件时，根据需要配置，具体见code/bochsrc.dist文件

bochs模拟了硬件

这里需要添加从硬盘启动的，硬盘信息
```
ata0-master: type=disk, mode=flat, path="/home/john/os/hd30M.img", cylinders=60, heads=16, spt=63
```

# 运行虚拟机

* 制定配置文件运行
```
$bochs -f bochsrc.dist
```

![](../02_mbr_hd/imgs/start.jpg)

* 按6开始模拟

![](../02_mbr_hd/imgs/start2.jpg)

* 再按c运行起来

![](../02_mbr_hd/imgs/os.jpg)

* 遇到模拟器卡死情况，kill杀死

![](../02_mbr_hd/imgs/kill.jpg)

# 分析

硬盘结构如下

![](../02_mbr_hd/imgs/xx.jpg)

实模式下的1MB内存布局

http://book.51cto.com/art/201604/509566.htm

硬盘当成一个IO设备，其有硬盘控制器（I/O接口）,就像显示器一样，其有显卡（也称为显示适配器），显存

我们操作了 用于文本模式显示适配器 ，其在1M物理地址下的开始地址是 0xB8000（有32KB大小）。

* 首先需要明确：对0xb8000这个内存地址写入内容，就可以在屏幕上输出文本;
* 本例我们使用gs寄存器存储了0xb8000这个地址，loader则存到磁盘的第2扇区，其操作了gs寄存器;
* mbr操作磁盘第二扇区（即loader），读取的内容存到0x900这个内存地址中;
* 此后，当mbr jmp到0x900这个内存地址时，就会执行0x900这块内存的指令，也就是是loader中的内容，也就是操作0xb8000这个内存地址，也就是向屏幕中显示文本。

# 参考

* x86 显示相关

http://blog.csdn.net/yh121212/article/details/18778313

http://blog.csdn.net/longintchar/article/details/70183677
