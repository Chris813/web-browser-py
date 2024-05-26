import socket
import ssl
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

def show(body):
    in_tag=False
    for c in body:
        if c=="<":
            in_tag=True
        elif c==">":
            in_tag=False
        else:
            if not in_tag:
                print(c,end="")

def load(url):
    body=url.request()
    show(body)

if __name__=="__main__":
    import sys
    url=URL(sys.argv[1])
    load(url)