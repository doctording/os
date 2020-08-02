注意在32bit平台下运行

编译所有文件
make all

将文件写入磁盘(注意文件路径等)
make image

bochs配置文件bochsrc.disk,如下命令运行
```
bochs -f bochsrc.disk
```