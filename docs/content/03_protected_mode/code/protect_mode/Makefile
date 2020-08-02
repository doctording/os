.PHONY:build image clean

mbr_src=mbr.S
loader_src=loader.S
mbr=mbr.bin
loader=loader.bin
img=/home/john/os/hd30M.img

all:build image

build:
	nasm -I include/ -o $(mbr) $(mbr_src)
	nasm -I include/ -o $(loader) $(loader_src)

## boot.img，30MB大小,前512字节是MBR

image:
	@-rm -rf $(img)
	bximage -hd -mode="flat" -size=30 -q $(img)
	dd if=$(mbr) of=$(img) bs=512 count=1 conv=notrunc
	dd if=$(loader) of=$(img) bs=512 seek=2 count=4 conv=notrunc

clean:
	rm -rf *.img *.bin
