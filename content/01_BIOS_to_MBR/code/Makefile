.PHONY:build image clean
 
obj=mbr.bin

build:
	nasm mbr.S -o $(obj)

## boot.img，30MB大小=30*1024*2*512B=61440*512B，前512字节是MBR
#1 先制作一个空的软盘映像文件diska.img
#2 制作一个包含boot.bin的映像文件boot.img
#3 将diska.img中1个扇区后面的数据拷贝到boot.img的后面

image:
	dd if=/dev/zero of=diska.img bs=512 count=61440
	dd if=$(obj) of=boot.img bs=512 count=1
	dd if=diska.img of=boot.img skip=1 seek=1 bs=512 count=61439

clean:
	rm -rf *.img $(obj)
