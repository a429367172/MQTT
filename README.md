# MQTT
use MQTT server to send and receive humidity and temperature information from the sensor
## 环境
1.订阅者使用python编写（需要paho-mqtt模块）  
2.服务器使用Apollo，win10  
3.发布者使用mosquitto_pub程序，需要移植到ARM板上  
## 要求
在物联网试验箱上实现一个温湿度显示系统，系统上电启动后自动启动此程序。每隔2秒自动刷新温湿度数据。温湿度数据从物联网试验箱自带的温湿度传感器获取。温湿度显示界面采用QT编程技术实现。搭建一个消息中间件服务器（使用MQTT类开源软件），在手机或电脑客户端可以实时获取温湿度信息。消息中间件客户端要求移植在试验箱开发板上，另一个客户端位于电脑或手机上。
## 步骤
### 1.服务器端
在Windows10下使用Apache Apollo搭建MQTT服务器，传输发布者与订阅者之间的信息，具体步骤为：  
（1）在apollo根目录下打开终端，输入create mybroke  
会发现根目录下多了一个叫myborke的文件夹  
![image](https://github.com/a429367172/MQTT/blob/master/demo/demo1.png)

（2）然后运行\apache-apollo-1.7.1\bin\mybroke\bin>apollo-broker.cmd  run开启服务器  
![image](https://github.com/a429367172/MQTT/blob/master/demo/demo2.png)
![image](https://github.com/a429367172/MQTT/blob/master/demo/demo3.png)

看到INFO | Accepting connections at: tcp://0.0.0.0:61613表示tcp服务启动成功，端口为61613。  
注：若端口被占用则可以使用netstat -ano | findstr 61613命令查找占用端口的进程(设进程号为12345)，然后使用taskkill /pid 12345 /f关闭此进程，若提示拒绝访问则使用管理员身份运行终端。  
（3）登录https://127.0.0.1:61681 ，默认用户名与密码为：admin、password，登录后可以看到如下界面：  
![image](https://github.com/a429367172/MQTT/blob/master/demo/demo4.png)

此时服务器启动成功，在Connectors中可以查看客户端的连接情况  
### 2.客户端1——发布者
（1）烧写CC2530温湿度光照传感器和协调器，二者之间使用ZigBee协议进行通信。  
![image](https://github.com/a429367172/MQTT/blob/master/demo/demo5.png)

（2）在Red Hat6.0系统上利用QT4进行开发。编写串口收发程序通过串口与协调器之间进行通信，协调器通过ZigBee协议接收温湿度光照传感器传来的温湿度信息，然后通过串口发送给网关。串口数据准备好时会发送一个信号，相应的槽函数会对串口数据进行操作。  
并编写UI界面和消息发布函数。  
（3）在开发板上运行qt程序，显示串口发来的温湿度信息：  
![image](https://github.com/a429367172/MQTT/blob/master/demo/demo6.png)
![image](https://github.com/a429367172/MQTT/blob/master/demo/demo7.png)

（4）点击submit，使用QProcess调用mosquito_pub，将温湿度信息发布到服务器  
![image](https://github.com/a429367172/MQTT/blob/master/demo/demo8.png)

### 3.客户端2——订阅者
订阅者客户端是用python语言编写，python中paho.mqtt模块包含MQTT客户端的基本操作，通过设置ip、端口、topic连接服务器，并订阅topic，利用on_connect、on_message回调函数设置连接时、接收消息时的操作。  
这一步中需要编写订阅者程序接收服务器上的信息，通过UI界面显示给用户：  
![image](https://github.com/a429367172/MQTT/blob/master/demo/demo9.png)
