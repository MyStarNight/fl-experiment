# 树莓派批量配置

# Part1：Base文件配置

参考文档：[制作SD卡备份镜像以及还原_sd卡镜像制作](https://blog.csdn.net/sinat_33909696/article/details/116430895)

在Ubuntu系统下，对base的系统进行拷贝；选择Ubuntu的原因是因为可以不关注tf卡的大小。

使用`df -h`指令查看是否已经挂载，以及sd卡所在的位置。

接下来就是使用指令备份：

	sudo dd if=/dev/sdb | gzip>/home/ngii/work/raspi_base/raspi_base.gz

# Part2： 写入sd卡

打开windows使用
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTg5MzU1MzIzOV19
-->