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

## 2023-10-23 test

在本次的测试中，成功调通了Windows和三个Raspi的联邦学习训练方式。

Windows打开指定文件夹

	cd E:\2023mem\Python-PJ\pysyft\Pysyft-0.2.4\examples\tutorials\advanced\websockets-example-MNIST-parallel

Raspi打开指定文件夹

	cd /home/pi/work/fl-pj/Pysyft-0.2.4/examples/tutorials/advanced/websockets-example-MNIST-parallel

### Raspi运行

node1: 192.168.3.33
	
	python run_websocket_server.py --host '192.168.3.33' --port 8777 --id alice
	
node2: 192.168.3.34

	python run_websocket_server.py --host '192.168.3.34' --port 8778 --id bob

node3: 192.168.3.38
	
	python run_websocket_server.py --host '192.168.3.38' --port 8779 --id charlie

### windows运行

	python run_websocket_server.py --host '192.168.3.30' --port 8780 --id testing --testing

### Jupyter Notebook
首先运行代码

	jupyter notebook

修改`in[7]`中代码
	  
	kwargs_websocket = {"host": "192.168.3.33", "hook": hook, "verbose": args.verbose}  
	alice = WebsocketClientWorker(id="alice", port=8777, **kwargs_websocket) 
	
	kwargs_websocket = {"host": "192.168.3.34", "hook": hook, "verbose": args.verbose}  
	bob = WebsocketClientWorker(id="bob", port=8778, **kwargs_websocket)
	
	kwargs_websocket = {"host": "192.168.3.38", "hook": hook, "verbose": args.verbose} 
	charlie = WebsocketClientWorker(id="charlie", port=8779, **kwargs_websocket)

	kwargs_websocket = {"host": "192.168.3.30", "hook": hook, "verbose": args.verbose} 
	testing = WebsocketClientWorker(id="testing", port=8780, **kwargs_websocket)

	worker_instances = [alice, bob, charlie ]

### 实验示意图

```mermaid
graph
A[Laptop]

```
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTQ2MjAyOTQzOCwxMjEyMDE4NDI0LDE5Mz
k1MzI4MTAsMTE0NzIxNjAxNCwtMTIyNTgzMzMzNywxMDM5OTAw
Njk1LC0xMzM1MjczMDQ5LDcyNDcxOTkzLC01NzYzODI0MDgsLT
E3ODE2NjA2NDddfQ==
-->