# 实验记录

## 2023-10-14 record
目前已经在Laptop（windows）、两个RasPi上安装了同样的环境

## 2023-10-17 test
打开指定文件夹：
	
	cd E:\2023mem\Python-PJ\pysyft\Pysyft-0.2.4\examples\tutorials\advanced\websockets-example-MNIST-parallel


运行测试指令

	python run_websocket_server.py --host '192.168.3.30' --port 8777 --id alice
	python run_websocket_server.py --host '192.168.3.30' --port 8778 --id bob
	python run_websocket_server.py --host '192.168.3.30' --port 8779 --id testing --testing


<!--stackedit_data:
eyJoaXN0b3J5IjpbLTEyMjU4MzMzMzcsMTAzOTkwMDY5NSwtMT
MzNTI3MzA0OSw3MjQ3MTk5MywtNTc2MzgyNDA4LC0xNzgxNjYw
NjQ3XX0=
-->