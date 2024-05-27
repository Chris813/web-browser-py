import tkinter

WIDTH, HEIGHT = 800, 600
window = tkinter.Tk()
# 在窗口内创建Canvas画布
canvas=tkinter.Canvas(window,width=WIDTH,height=HEIGHT)
tkinter.mainloop()
# 事件循环
while True:
    for evt in pendingEvents():
        handleEvent(evt)
    drawScreen()

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        # 在窗口内创建Canvas画布
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        
        self.canvas.pack()
    def load(self,url):
        self.canvas.create_rectangle(10,20,400,300)
        self.canvas.create_oval(100,100,150,150)
        self.canvas.create_text(200,150,text="hello")

if __name__=="__main__":
    import sys
    Browser().load(Url(sys.argv[1]))