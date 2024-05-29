use python3 to implement a simple browser.

online book：https://browser.engineering/

# Notes

## Part1:Drawing Graphics

### Downloading Web Pages

代码实现：`browser.py`

本章完成了：

- 将 URL 解析为方案、主机、端口和路径;
- 使用`sockets`和  `ssl`  库连接到该主机;

  使用 SSLContext 实例的 SSLContext.wrap_socket() 来将套接字包装为 SSLSocket 对象

  ```
  ctx=ssl.create_default_context()
  s=ctx.wrap_socket(s,server_hostname=self.host)
  ```

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

### Formatting Text

tkinter 的字符对象`Font`，可以设置字体、样式、粗细等属性

```python
bi_times = tkinter.font.Font(
            family="Times",
            size=16,
            weight="bold",
            slant="italic",
        )
# 使用Font对象
canvas.create_text(200, 100, text="Hi!", font=bi_times)
```

**测量文本**

```bash
>>> bi_times.metrics()
{'ascent': 15, 'descent': 4, 'linespace': 19, 'fixed': 0}
>>> bi_times.measure("Hi!")
24
```

- metrics()：返回一个字典，包含了字体的度量信息
  - `ascent`：字符的上升高度，从基线到字符顶部的距离
  - `descent`：字符的下降高度，从基线到字符底部的距禿
  - `linespace`：行间距，字符的上升高度和下降高度之和
  - `fixed`：固定宽度，如果为 0，则字符宽度不固定
- measure(text)：返回文本的宽度

通过上面的函数给出的度量信息，可以计算出文本的高度和宽度，从而实现文本的布局，但是由于默认的绘制坐标以文本的中心为基准，所以如果文本宽度不一样，会导致文本重叠。通过设置`anchor`属性，可以设置文本的对齐方式

```python
x, y = 200, 225
canvas.create_text(x, y, text="Hello, ", font=font1, anchor='nw')
x += font1.measure("Hello, ")
canvas.create_text(x, y, text="overlapping!", font=font2, anchor='nw')
```

1. 改进布局函数
   根据字体对象的度量信息，计算文本的高度和宽度，实现文本的布局。

对于英文文本，根据空格进行分割

```python
def layout(text):
    font=tkinter.font.Font()
    display_list=[]
    cursor_x,cursor_y=HSTEP,VSTEP
    for word in text.split():
        w=font.measure(word)
        display_list.append((cursor_x,cursor_y,word))
        cursor_x+=w+font.measure(" ")
        if cursor_x+w>=WIDTH-HSTEP:
            cursor_y+=font.metrics("linespace")*1.25
            cursor_x=HSTEP
    return display_list
```

2. 为文本添加样式

解析 HTML 标签，为文本添加样式，如加粗、斜体、下划线等。之前的 lex 函数只解析标签内的文本，现在可以解析标签，返回一个 token 列表，包含标签和文本。

```python
def lex(body):
    out=[]
    buffer=""
    in_tag=False
    for c in body:
        if c=="<":
            in_tag=True
            if buffer:out.append(Text(buffer))
            buffer=""
        elif c==">":
            in_tag=False
            out.append(Tag(buffer))
            buffer=""
        else:
            buffer+=c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out
```

忽略空文本，不忽略空标签

3. 重构布局函数

布局需要根据标签的属性，设置文本的样式，如字体、大小、颜色等。通过设置字体对象的属性，实现文本的样式。

通过一个 Layout 对象，由于 token 是一个列表，布局函数顺序遍历，文本在标签中间

```python
class Layout:
    def __init__(self,tokens):
        self.display_list=[]
        self.cursor_x,self.cursor_y=HSTEP,VSTEP
        self.weight="normal"
        self.style="roman"
        self.size=12
        for tok in tokens:
            self.token(tok)
    def token(self,tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                # 把文本加入绘制列表
                self.word(word)
        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4

    def word(self,word):
        font=tkfont.Font(size=self.size,weight=self.weight,slant=self.style)
        w=font.measure(word)
        self.display_list.append((self.cursor_x,self.cursor_y,word,font))
        self.cursor_x+=w+font.measure(" ")
        if self.cursor_x+w>=WIDTH-HSTEP:
            self.cursor_y+=font.metrics("linespace")*1.25
            self.cursor_x=HSTEP

```

把字体参数作为属性，根据读取的标签进行修改，在存入绘制列表时时，根据字体的属性，设置文本的样式。

4. 不同大小的文本对齐

现在呈现出来的文本由于大小不一致，文本沿其顶部对齐。
![Alt text](/imgs/image.png)

两阶段布局：

- 第一阶段：识别一行中的文本并计算它们的 x 位置
- 第二阶段：计算 y 位置，使得文本垂直对齐

```python
    def word(self,word):
        font=tkfont.Font(size=self.size,weight=self.weight,slant=self.style)
        w=font.measure(word)
        # 一整行则计算该行的y坐标
        if self.cursor_x+w>=WIDTH-HSTEP:
            self.flush()
        # 行内的token计算x坐标并记录
        self.line.append((self.cursor_x,word,font))
        self.cursor_x+=w+font.measure(" ")
    def flush(self):
        if not self.line:
            return
        metrics=[font.metrics() for x,word,font in self.line]
        max_ascent=max([m["ascent"] for m in metrics])
        baseline=self.cursor_y+max_ascent
        for x,word,font in self.line:
            y=baseline-font.metrics("ascent")
            self.display_list.append((x,y,word,font))
        max_descent=max([m["descent"] for m in metrics])
        self.cursor_y=baseline+1.25*max_descent
        self.cursor_x=HSTEP
        self.line=[]
```

注意在其它需要换行的地方调用 flush() 函数

5. 缓存字体

文本布局很慢，尽量重用 Font 对象，避免重复创建

```python
FONTS={}

def get_font(size,weight,style):
    key=(size,weight,style)
    if key not in FONTS:
        font=tkfont.Font(size=size,weight=weight,slant=style)
        label=tkinter.Label(font=font)
        FONTS[key]=(font,label)
    return FONTS[key][0]
```

通过一个字典保存 Font 对象，如果字典中没有对应的 Font 对象，则创建一个新的 Font 对象，并保存到字典中。

#### 总结

本章添加了解析标签的功能，根据标签设置文本渲染样式；通过字体对象控制文本的样式。

通过 Layout 类，将标签代表的文本样式作为属性存储。

通过两阶段布局，实现不同大小文本的对齐。

## Part 2: Viewing Documents

### Constructing a Document Tree

之前的章节中将 HTML 解析为标签和文本的流，现在需要将这些标签和文本组织成树形结构，以便于后续的处理。

1. 修改 Text 类和 Tag 类，添加 parent、children 属性

```python
class Text:
    def __init__(self,text):
        self.text=text
        self.children=[]
        self.parent=parent

class Element:
    def __init__(self,tag):
        self.tag=tag
        self.children=[]
        self.parent=parent
```

2. 解析 HTML 为树形结构

注意解析第一个和最后一个标签的边界情况

```python
class HTMLParser:
    def __init__(self,body):
        self.body=body
        # 用栈来存储不完整的节点
        self.unfinished=[]

    def parse(self):
        text=""
        in_tag=False
        for c in self.body:
            if c=="<":
                in_tag=True
                # 进入tag内部，此时如果有text就是文本节点解析完成
                if text:
                    self.add_text(text)
                #开始解析tag内部
                text=""
            elif c==">":
                in_tag=False
                self.add_tag(text)
                text=""
            else:
                text+=c
        if not in_tag and text:
            self.add_text(text)
        return self.finish()
    def add_text(self,text):
        # 文本Token：将该节点加入到 DOM 树中，父节点就是当前栈顶对应的DOM节点。文本 Token 不需要压入到栈中
        parent=self.unfinished[-1]
        node=Text(text.parent)
        parent.children.append(node)
    def add_tag(self,tag):
        if text.startswith("/"):
            # endTag 从栈中弹出一个节点，表示该节点解析完成。父节点为当前栈顶节点，将其加入到DOM树中
            # 边界情况：最后一个标签的时候，栈只剩下一个节点
            if len(self.unfinished)==1: return
            node=self.unfinished.pop()
            parent=self.unfinished[-1]
            parent.children.append(node)
        else:
            # startTag 父元素就是当前栈顶对应的DOM节点。将这个token入栈
            # 边界情况：第一个标签的时候，栈为空
            parent=self.unfinished[-1] if self.unfinished else None
            node=Element(tag,parent)
            self.unfinished.append(node)
```

> Go Further
> 在传统的浏览器中，HTML 解析器运行于主线程之中，并且在遇到 </script> 标签后会被阻塞，直到脚本从网络中被获取和执行。为了防止解析 HTML 被 js 脚本阻塞的问题，浏览器采用了预解析技术。

3. 优化 HTML 解析器

- 忽略！开头的标签和空文本
- 添加对自闭合标签的支持
- 将标签的 tag 名和属性分开
  ```python
      def get_attributes(self,text):
      parts=text.split()
      tag=parts[0].casefold()
      attributes={}
      for attrpair in parts[1:]:
          if "=" in attrpair:
              key,value=attrpair.split("=",1)
              attributes[key]=value
              if len(value)>2 and value[0] in ["'",'\"']:
                  value=value[1:-1]
          else:
              attributes[attrpair.casefold()]=""
      return tag,attributes
  ```

4. 修改布局类处理 DOM 树节点

   使用递归遍历 DOM 树，计算文本节点的布局

   ```python
       def recurse(self,tree):
           if isinstance(tree,Text):
               for word in tree.text.split():
                   # 为每一个单词计算坐标，加入绘制列表
                   self.word(word)
           else:
               self.open_tag(tree.tag)
               # 深度优先遍历
               for child in tree.children:
                   self.recurse(child)
               self.close_tag(tree.tag)
       def open_tag(self,tag):
           if tag == "i":
               self.style = "italic"
           elif tag == "b":
               self.weight = "bold"
           elif tag == "small":
               self.size -= 2
           elif tag == "big":
               self.size += 4
           elif tag == "br":
               self.flush()
       def close_tag(self, tag):
           if tag == "i":
               self.style = "roman"
           elif tag == "b":
               self.weight = "normal"
           elif tag == "small":
               self.size += 2
           elif tag == "big":
               self.size -= 4
           elif tag == "p":
               self.flush()
               self.cursor_y += VSTEP
   ```

5. 对于省略的隐式标签进行补全

   在解析 HTML 的同时处理 HTML 格式错误

#### 总结

本章终于将 HTML 字符流转换成 DOM 树结构。

将 HTML 标记转换为树的解析器，改进布局算法，使用递归遍历 HTML 树进行布局

用于识别和处理元素属性的代码

自动修复一些格式错误的 HTML 文档
