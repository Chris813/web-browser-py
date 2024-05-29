import socket
import ssl
import tkinter
from tkinter import font as tkfont

def print_tree(node,indent=0):
    # print(node)
    print(" " * indent + str(node))
    for child in node.children:
        print_tree(child,indent+2)


class Text:
    def __init__(self,text,parent):
        self.text=text
        self.children=[]
        self.parent=parent
    def __repr__(self):
        return repr(self.text)

class Element:
    def __init__(self,tag,attributes,parent):
        self.tag=tag
        self.children=[]
        self.parent=parent
        self.attributes=attributes
    def __repr__(self):
        # print("here")
        return "<"+self.tag+">"

#定义HTML解析器
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
    def add_text(self,text):
        # 跳过空文本
        if text.isspace(): return
        self.implicit_tags(None)
        # 文本Token：将该节点加入到 DOM 树中，父节点就是当前栈顶对应的DOM节点。文本 Token 不需要压入到栈中
        parent=self.unfinished[-1]
        node=Text(text,parent)
        parent.children.append(node)
    SELF_CLOSED_TAGS=[
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    ]
    def add_tag(self,tag):
        # 忽略！开头的标签
        if tag.startswith("!"): return
        tag,attributes=self.get_attributes(tag)
        self.implicit_tags(tag)
        if tag.startswith("/"):
            # endTag 从栈中弹出一个节点，表示该节点解析完成。父节点为当前栈顶节点，将其加入到DOM树中
            # 边界情况：最后一个标签的时候，栈只剩下一个节点
            if len(self.unfinished)==1: return 
            node=self.unfinished.pop()
            parent=self.unfinished[-1]
            parent.children.append(node)
        elif tag in self.SELF_CLOSED_TAGS:
            parent=self.unfinished[-1]
            node=Element(tag,attributes,parent)
            parent.children.append(node)
        else:
            # startTag 父元素就是当前栈顶对应的DOM节点。将这个token入栈
            # 边界情况：第一个标签的时候，栈为空
            parent=self.unfinished[-1] if self.unfinished else None
            node=Element(tag,attributes,parent)
            self.unfinished.append(node)
    
    HEAD_TAGS = [
        "base", "basefont", "bgsound", "noscript",
        "link", "meta", "title", "style", "script",
    ]

    def implicit_tags(self,tag):
        while True:
            # 每次循环只添加一个隐式标记
            open_tags = [node.tag for node in self.unfinished]
            # 省略html标签
            if open_tags == [] and tag != "html":
                self.add_tag("html")
            # 
            elif open_tags == ["html"] \
                 and tag not in ["head", "body", "/html"]:
                if tag in self.HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif open_tags == ["html", "head"] and \
                 tag not in ["/head"] + self.HEAD_TAGS:
                self.add_tag("/head")
            else:
                break 
    def finish(self):
        if not self.unfinished:
            self.implicit_tags(None)
        while len(self.unfinished)>1:
            node=self.unfinished.pop()
            parent=self.unfinished[-1]
            parent.children.append(node)
        return self.unfinished.pop()
# def lex(body):
#     out=[]
#     buffer=""
#     in_tag=False
#     for c in body:
#         if c=="<":
#             in_tag=True
#             if buffer:out.append(Text(buffer))
#             buffer=""
#         elif c==">":
#             in_tag=False
#             out.append(Tag(buffer))
#             buffer=""
#         else:
#             buffer+=c
#     if not in_tag and buffer:
#         out.append(Text(buffer))
#     return out

FONTS={}

def get_font(size,weight,style):
    key=(size,weight,style)
    if key not in FONTS:
        font=tkfont.Font(size=size,weight=weight,slant=style)
        label=tkinter.Label(font=font)
        FONTS[key]=(font,label)
    return FONTS[key][0]

class Layout:
    def __init__(self,tree):
        self.display_list=[]
        #存储当前行的所有文本
        self.line=[]
        self.cursor_x,self.cursor_y=HSTEP,VSTEP
        self.weight="normal"
        self.style="roman"
        self.size=12
        # for tok in tokens:
        #     self.token(tok)
        #最后可能不足一整行，把最后一行加入绘制列表
        while tree:
            if tree.tag=='body':
                self.recurse(tree)
                break
            else:
                for child in tree.children:
                    tree=child

        self.flush()
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
        elif tag in ["br","p"]:
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
        elif tag in ["p","li"]:
            self.flush()
            self.cursor_y += VSTEP
    # def token(self,tok):
    #     if isinstance(tok, Text):
    #         for word in tok.text.split():
    #             # 把文本加入绘制列表
    #             self.word(word)
    #     elif tok.tag == "i":
    #         self.style = "italic"
    #     elif tok.tag == "b":
    #         self.style = "roman"
    #     elif tok.tag == "b":
    #         self.weight = "bold"
    #     elif tok.tag == "/b":
    #         self.weight = "normal"
    #     elif tok.tag == "small":
    #         self.size -= 2
    #     elif tok.tag == "/small":
    #         self.size += 2
    #     elif tok.tag == "big":
    #         self.size += 4
    #     elif tok.tag == "/big":
    #         self.size -= 4
    #     elif tok.tag == "br":
    #         self.flush()
    #     elif tok.tag == "/p":
    #         self.flush()
    #         self.cursor_y += VSTEP
    
    def word(self,word):
        font=get_font(self.size,self.weight,self.style)
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


WIDTH, HEIGHT = 800, 600
HSTEP,VSTEP=13,18
SCROLLSTEP=100
class URL:
    def __init__(self,url):
        # Split the URL into scheme and url
        # e.g. http://www.google.com/xxx -> scheme=http, url=www.google.com/xxx
        self.scheme,url=url.split('://',1)
        # Check if the scheme is http or https
        assert self.scheme in ["http","https"]
        if self.scheme=="https":
            self.port = 443
        elif self.scheme=="http":
            self.port = 80
        # Split the url into host and path
        if "/" not in url:
            url=url+"/"
        self.host,url=url.split('/',1)
        self.path="/"+url
        if ":" in self.host:
            self.host,port=self.host.split(":",1)
            self.port=int(port)
    # 通过套接字发送请求
    def request(self):
        # Create a socket,explained this function
        # socket(socket_family, socket_type, protocol=0)
        # socket_family: 主要包含AF_INET、AF_INET6、AF_UNIX
        # socket_type: 主要包含SOCK_STREAM、SOCK_DGRAM、SOCK_RAW
        # protocol: 用于指定创建套接字的协议，通常默认省略值为0
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM,proto=socket.IPPROTO_TCP)
        if self.scheme=="https":
            ctx=ssl.create_default_context()
            s=ctx.wrap_socket(s,server_hostname=self.host)
        s.connect((self.host,self.port))
        # Send the request
        # s.send(string[, flag])
        # 发送TCP套接字的数据，将string中的数据发送到连接的套接字；返回值是发送到另一台计算机的数据字节数，该数量可能小于string的字节大小
        request="GET {} HTTP/1.0\r\n".format(self.path)
        request+="Host: {}\r\n".format(self.host)
        request+="\r\n"
        # request.encode("utf-8")将字符串转换为utf-8编码的bytes
        s.send(request.encode("utf-8"))
        # Receive the response
        # s.makefile(mode, buffering)返回一个与套接字关联的文件对象，该文件对象可以用于读取和写入数据
        response=s.makefile("r",encoding="utf-8",newline="\r\n")
        statusline=response.readline()
        version,status,explanation=statusline.split(" ",2)
        response_headers={}
        while True:
            line=response.readline()
            if line=="\r\n":
                break
            header,value=line.split(":",1)
            response_headers[header.lower()]=value.strip()
        assert "transfer-encoding" not in response_headers
        assert "content-length" in response_headers
        content=response.read()
        s.close()
        return content
    
class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        # 在窗口内创建Canvas画布
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.scroll=0
        self.window.bind("<Down>",self.scrolldown)
        self.window.bind("<MouseWheel>",self.mousescroll)
        self.window.bind("<Up>",self.scrollup)
    def scrolldown(self,e):
        self.scroll+=SCROLLSTEP
        self.draw()
    def scrollup(self,e):
        if self.scroll-SCROLLSTEP>=0:
            self.scroll-=SCROLLSTEP
            self.draw()
    def mousescroll(self,e):
        # print(e.delta)
        if e.delta<0:
            self.scroll+=SCROLLSTEP
        else:
            if self.scroll-SCROLLSTEP>=0:
                self.scroll-=SCROLLSTEP
        self.draw()
    def load(self,url):
        body=url.request()
        # 返回一个树的顶点
        self.nodes=HTMLParser(body).parse()
        # print_tree(self.nodes)
        self.display_list=Layout(self.nodes).display_list
        self.draw()
    #绘制，需要访问canvas
    def draw(self):
        # 刷新前清除画布
        self.canvas.delete("all")
        for x,y,c,f in self.display_list:
            # 超出画布范围，不绘制
            if y>self.scroll+HEIGHT:
                continue
            if y+VSTEP<self.scroll:
                continue
            # y-self.scroll表示偏移量
            self.canvas.create_text(x, y-self.scroll, text=c,font=f,anchor="nw")
if __name__=="__main__":
    import sys
    # body=URL(sys.argv[1]).request()
    # nodes=HTMLParser(body).parse()
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()
    # print_tree(nodes)