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

### Drawing to the Screen

本章通过 python 自带的 GUI 库 Tkinter 实现了一个简单的浏览器界面。从基本的命令行浏览器转变为带有可滚动文本的图形用户界面

- 使用`Tkinter`库创建一个窗口,使用 Canvas 绘制
  ```python
  def __init__(self):
    self.window = tkinter.Tk()
    # 在窗口内创建Canvas画布
    self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
    self.canvas.pack()
  ```
- 通过水平和垂直偏移量布局文本，存入绘制列表

  ```python
  def layout(text):
      display_list=[]
      cursor_x,cursor_y=HSTEP,VSTEP
      for c in text:
          display_list.append((cursor_x,cursor_y,c))
          cursor_x+=HSTEP
          if cursor_x>=WIDTH-HSTEP:
              cursor_y+=VSTEP
              cursor_x=HSTEP
      return display_list
  ```

- 监听键盘命令，实现滚动响应

  发生滚动事件时，更新偏移量，重新绘制文本

  ```python
  def scrolldown(self,e):
    self.scroll+=SCROLLSTEP
    self.draw()
  def draw(self):
    # 刷新前清除画布
    self.canvas.delete("all")
    for x,y,c in self.display_list:
        # 超出画布范围，不绘制
        if y>self.scroll+HEIGHT:
            continue
        if y+VSTEP<self.scroll:
            continue
        # y-self.scroll表示偏移量
        self.canvas.create_text(x, y-self.scroll, text=c)
  ```

> Go Further

- Firefox 和 Chrome 使用 ICU —— International Components for Unicode，一个开源的 Unicode 库，用于处理文本和字符集。ICU 使用动态编程根据词频表猜测短语边界。
- 存储显示列表可以使滚动速度更快，浏览器不会在每次滚动时重新布局。滚动是最常见的用户与网页的交互。因此，真正的浏览器投入了大量的时间来提高速度
  https://hacks.mozilla.org/2017/10/the-whole-web-at-maximum-fps-how-webrender-gets-rid-of-jank/

> Exercises

- [ ] 布局美化：换行
- [x] 滚动优化：添加键盘上键的绑定，实现向上滚动；添加鼠标滚轮事件，实现上下滚动：<MouseWheel>，监听 event.delta 值，<0 向下滚动，>0 向上滚动
- [ ] 可以改变窗口大小，同时窗口内的内容重新布局
- [ ] 添加一个 scrollbar，实现滚动条的滚动
- [ ] 支持绘制 emoji： 基于 OpenMoji 项目
- [ ] 添加错误处理：对应错误 URL
- [ ] 支持其它方向的文本排版
