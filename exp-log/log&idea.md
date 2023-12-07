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
B[node1:raspi 4B] -- training --> E((weight)) --> A[Laptop]
C[node2:raspi 4B] -- training--> F((weight))  --> A
D[node3:raspi 400] -- training--> G((weight))  --> A
A-->H((model))
H--testing-->I(accuracy)
```

## 2023-10-30 test

在目前的华为路由器上一共连接了10台树莓派；

树莓派运行指令如下：

	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.33' --port 9292 --id A
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.38' --port 9292 --id B
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.40' --port 9292 --id C
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.41' --port 9292 --id D
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.42' --port 9292 --id E
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.43' --port 9292 --id F
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.44' --port 9292 --id G
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.45' --port 9292 --id H
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.46' --port 9292 --id I
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.47' --port 9292 --id J

Windows运行指令如下：

	python .\run_websocket_server.py --host '192.168.3.39' --port 9292 --id testing --testing

## 2023-11-03 test
树莓派命令简化

创建了`start.vbs`脚本批量打开命令行。

在树莓派上建立脚本文件`server.sh`，自动运行挂起服务，步骤如下：

首先创建文件

	vim server.sh

然后输入树莓派自己的挂起指令

	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.33' --port 9292 --id A
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.38' --port 9292 --id B
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.40' --port 9292 --id C
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.41' --port 9292 --id D
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.42' --port 9292 --id E
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.43' --port 9292 --id F
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.44' --port 9292 --id G
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.45' --port 9292 --id H
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.46' --port 9292 --id I
	cd /home/pi/work/fl-pj/fl-demo; python run_websocket_server.py --host '192.168.3.47' --port 9292 --id J

最后一步

	chmod +x server.sh

创建成功。

挂起服务器只需要运行：

	./server.sh


##  2023-12-7 ideas

当前Federated Learning Plarform已经搭建完成，并在联邦学习的框架下加入了Continual Learning算法。

**Short Term**：如果需要进一步发展，有以下几个发展方向：

1. Decentrialized Fedarated Learning:去中心化
2. 基于分簇的FL
3. RealFL：利用设备的异构性去实现一个实际的Federated
4. 设备的可获得性（accessibility）

**Long Term**

1. 尝试加入一些算法，比如强化学习算法（FRL）

**Dataset**
 
> https://github.com/waico/SkAB

胡姐提供的一个数据集，
<!--stackedit_data:
eyJoaXN0b3J5IjpbMjQ5MDk2ODI3LC04NjkxNDU1MTQsLTIwOT
M4NjQzOTcsMTY4NDk5MjAxMSwtMTUyMjkxNTg1NywtMjU0NTQw
OTI1LDExMzEwNDUxNTMsNzk0NTg3Mzg3LC0yMTYzOTU4NzMsLT
EzMTk4NDQ3ODUsLTI3NjcxMDY5OCwxNDYzNjYzNjkzLDE0NjIw
Mjk0MzgsMTIxMjAxODQyNCwxOTM5NTMyODEwLDExNDcyMTYwMT
QsLTEyMjU4MzMzMzcsMTAzOTkwMDY5NSwtMTMzNTI3MzA0OSw3
MjQ3MTk5M119
-->