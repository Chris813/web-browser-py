use python3 to implement a simple browser.

online book：https://browser.engineering/

# Notes

## Part1:Drawing Graphics

### Downloading Web Pages

代码实现：`browser.py`

本章完成了：

- 将 URL 解析为方案、主机、端口和路径;
- 使用`sockets`和  `ssl`  库连接到该主机;
- 向该主机发送 HTTP 请求，包括  `Host`  标头;
- 将 HTTP 响应拆分为状态行、标头和正文;
- 打印正文中的文本（而不是标签）。

知识点：

<aside>
💡 套接字：

`Socket`是进程间通信(`IPC`)的一种实现，允许位于不同主机甚至同一主机上不同进程之间进行通信。`socket`本质上是对`TCP/IP` 协议栈的封装，通过 socket 调用操作系统协议栈，包含进行网络通信必需的五种信息：连接使用的协议，本地主机的 IP 地址，本地进程的协议端口，对方主机的 IP 地址，对方进程的协议端口。

- 套接字可以简单理解为：套接字 = IP 地址 + 端口号
- 进程间通信的实现不只有`socket`，还有信号量、共享内存、消息队列等方式
</aside>

分类：

- 根据传输使用的协议类型
  - `SOCK_STREAM` 流式套接字，TCP
  - `SOCK_DGRAM` 数据报套接字，UDP
  - `SOCK_RAW` 裸套接字，
    • 不使用传输层协议，直接和底层进行数据传输，如`IP`
- 根据套接字地址家族
  - **IPv4 协议簇**(`AF_INET`)
    - 不同主机之间进行通信时使用
  - **IPv6 协议簇**(`AF_INET6`)
    - 不同主机之间进行通信时使用
  - **UNIX 协议簇**(`AF_UNIX`)
    - 同一主机上不同进程之间通信时使用
    - 不需要将数据向下传递，不占用`TCP`/`UDP`协议栈，提升传输效率

创建套接字：
`socket(socket_family, socket_type, protocol=0)`

```
# socket_family: 主要包含AF_INET、AF_INET6、AF_UNIX
# socket_type: 主要包含SOCK_STREAM、SOCK_DGRAM、SOCK_RAW
# protocol: 用于指定创建套接字的协议，通常默认省略值为0
# 创建TCP套接字
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM,proto=socket.IPPROTO_TCP)
```
