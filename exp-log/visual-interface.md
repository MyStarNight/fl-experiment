# 可视化操作界面要求

## 说明

当前共有10个设备一起进行训练，并使用一台Ubuntu进行模型聚合并更新模型到各个树莓派；同时Ubuntu也担任推理测试的作用。


# Ubuntu界面说明

## 开始-start
功能：联邦学习的开始界面，按下开始按钮以后，通过websocket连接各个树莓派，并开始我们的训练和测试。

按钮：start

## 训练阶段-stage
功能：stage是每次训练必不可少的参数，因为每次训练都需要在上一阶段训练完成的模型下接着训练，以此达到持续学习的目的。

按钮：stage

类型：int

## 随机种子-random seed
功能：由于神经网络最开始的权重初始化具有随机性，为了可以复现或者更好地观察其变化，我们需要设置随机数种子。

按钮：seed

类型：int

## 训练次数-round
功能：一个round是指一次模型聚合并更新；随着数据量的变化，我们训练的round也随之变化。

按钮：Training round

类型：int

# Raspi说明
Raspi只需要在后台进程中挂起websocket通信，并保证不会间断；同时在Raspi中，需要注意的是，每次要输入所执行的任务。
<!--stackedit_data:
eyJoaXN0b3J5IjpbNjAxMDgyMDU1LDE0MzUzODM1NzcsNTY3Mj
kwNDg4XX0=
-->