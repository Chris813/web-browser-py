import socket
import ssl
import tkinter
from tkinter import font as tkfont
class Text:
    def __init__(self,text):
        self.text=text

class Tag:
    def __init__(self,tag):
        self.tag=tag

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

FONTS={}

def get_font(size,weight,style):
    key=(size,weight,style)
    if key not in FONTS:
        font=tkfont.Font(size=size,weight=weight,slant=style)
        label=tkinter.Label(font=font)
        FONTS[key]=(font,label)
    return FONTS[key][0]

class Layout:
    def __init__(self,tokens):
        self.display_list=[]
        #存储当前行的所有文本
        self.line=[]
        self.cursor_x,self.cursor_y=HSTEP,VSTEP
        self.weight="normal"
        self.style="roman"
        self.size=12
        for tok in tokens:
            self.token(tok)
        #最后可能不足一整行，把最后一行加入绘制列表
        self.flush()
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
        elif tok.tag == "br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP
    
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
        tokens=lex(body)
        self.display_list=Layout(tokens).display_list
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
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()