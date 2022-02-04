#!/usr/bin/python3


from base64 import b64decode, b64encode
from curses.textpad import Textbox
from tunnel import Tunnel
from curses import *
from time import sleep
from threading import Thread
from os import _exit
from Crypto.Cipher import AES

class UI(Tunnel):

    Topwin  = None 
    Mainwin = None
    Botwin  = None

    UserName = "Anonymous"

    Key = None
    IV  = None

    NotExit = True
    NotBreak = True

    MainColor = 0
    MsgColor  = 0


    offset = 0
    ps     = 0

    CreTime     = "00:00:00"
    OnlineUsers = 0

    def __init__(self):
        self.Topwin  = topw
        self.Mainwin = mainw
        self.Botwin  = botw

        self.GetReady()



    def GetReady(self):
        Banner = """
        ▄▄▄█████▓ ██░ ██ ▓█████     ██▀███   ▒█████   ▒█████   ███▄ ▄███▓
        ▓  ██▒ ▓▒▓██░ ██▒▓█   ▀    ▓██ ▒ ██▒▒██▒  ██▒▒██▒  ██▒▓██▒▀█▀ ██▒
        ▒ ▓██░ ▒░▒██▀▀██░▒███      ▓██ ░▄█ ▒▒██░  ██▒▒██░  ██▒▓██    ▓██░
        ░ ▓██▓ ░ ░▓█ ░██ ▒▓█  ▄    ▒██▀▀█▄  ▒██   ██░▒██   ██░▒██    ▒██ 
          ▒██▒ ░ ░▓█▒░██▓░▒████▒   ░██▓ ▒██▒░ ████▓▒░░ ████▓▒░▒██▒   ░██▒
          ▒ ░░    ▒ ░░▒░▒░░ ▒░ ░   ░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░▒░▒░ ░ ▒░   ░  ░
            ░     ▒ ░▒░ ░ ░ ░  ░     ░▒ ░ ▒░  ░ ▒ ▒░   ░ ▒ ▒░ ░  ░      ░
            ░       ░  ░░ ░   ░        ░░   ░ ░ ░ ░ ▒  ░ ░ ░ ▒  ░      ░   
            ░  ░  ░   ░  ░      ░         ░ ░      ░ ░         ░   

"""
        by = "          @BY: k4ito & 0xSYN\n"
        HelpPage = """
Usage:
        /connect    : Use /connect SERVER_IP_ADDR SERVER_PORT
                    : EX: /connect 111.111.111.111 1337
        /name       : Use /name YOURNAME to change your username.
                    : EX: /name s4msepi0l
        /join       : Use /join to join the room.
        /exit       : Use /exit to quit the room correctly. 
        \n\r  
"""
        self.Mainwin.addstr(Banner , RED)
        self.Mainwin.addstr(by , self.MainColor)
        self.Mainwin.addstr(HelpPage , self.MainColor)
        self.Refresh()
        self.RefreshBot()


        while self.NotExit:
            self.Refresh()
            self.RefreshBot()
            cmd = self.Botwin.getstr()
            self.HandleCommand(cmd.decode("ascii"))


    def HandleCommand(self , cmd):
        cmd = cmd.split(" ")
        if cmd[0] == "/exit":
            self.NotExit = False
            exit()
        
        elif cmd[0] == "/connect":
            try:
                self.IP   = str(cmd[1])
                self.PORT = int(cmd[2])
                self.Mainwin.addstr("Host: {}:{}\n".format(self.IP , self.PORT) , self.MainColor)
            except:
                self.Mainwin.addstr("Somthing wrong!\n" , RED | A_BOLD)
        
        elif cmd[0] == "/name":
            try:
                if len(cmd[1]) > 1:
                    self.UserName = cmd[1].rstrip("\n")
                    self.Mainwin.addstr("USERNAME: {}\n".format(self.UserName) , self.MainColor)
                else:
                    self.Mainwin.addstr("Somthing wrong!: very short name\n" , RED | A_BOLD)
            except:
                self.Mainwin.addstr("Somthing wrong!\n" , RED | A_BOLD)
        
        elif cmd[0] == "/join":
            if self.IP != "" and self.PORT != 0:
                try:
                    self.ConnectToServer()
                    Exist = self.CheckUserName(self.UserName)
                    if Exist:
                        self.Mainwin.addstr("[+] USERNAME {} is Already Exist , Please Change it.\n".format(self.UserName) , RED | A_BOLD)
                    else:
                        self.RoomPage()
                except:
                    self.Mainwin.addstr("Connection Refused [X]\nHOST: {}:{}\n".format(self.IP , self.PORT) , RED | A_BOLD)
            else:
                self.Mainwin.addstr("Somthing wrong!!\nHOST: {}:{} ; USERNAME: {}\n".format(self.IP , self.PORT , self.UserName) , RED | A_BOLD)
        else:
            self.Mainwin.addstr("Undifined command! {}\n".format(cmd[0]) , RED | A_BOLD)
  


    def RoomPage(self):
        self.HandleKeys()
        self.InitInfo()
        self.Mainwin.erase()
        self.RefreshTop()
        self.RefreshBot()
        self.Refresh()
        self.JoinMsg(self.UserName)
        self.HelpPage()
        self.MsgColor = YELLOW
        self.Start()
        
    

    def Start(self):
        st = Thread(target=self.StartSend)
        lt = Thread(target=self.StartListen)

        st.start()
        lt.start()
        st.join()
        lt.join()

    def StartListen(self):
        while 1:
            msg = self.Listen()
            if msg.decode()[:3] == ">>>":
                self.Mainwin.addstr(msg , GREEN | A_BOLD)
                self.InitInfo()
                self.RefreshTop()
            elif msg.decode()[:3] == "<<<":
                self.Mainwin.addstr(msg , RED | A_BOLD)
                self.InitInfo()
                self.RefreshTop()
            else:
                self.Mainwin.addstr(self.Decrypt(msg) , self.MsgColor)
            self.Refresh()

    def StartSend(self):
        self.Mainwin.addstr(">>> You JOINED!\n" , GREEN | A_BOLD)
        self.Refresh()
        self.RefreshBot()
        while 1:
            msg = self.Botwin.getstr()
            if msg.decode()[:5] == "/exit":
                self.ExitMsg(self.UserName)
                endwin()
                _exit(0)
            elif msg.decode()[:6] == "/color":
                self.ChangeColor(msg)
                self.RefreshTop()
                self.Refresh()
                self.RefreshBot()
            elif msg.decode()[:6] == "/clear":
                self.ClearScreen()
            elif msg.decode()[:5] == "/help":
                self.HelpPage()
            else:
                if len(msg) < 1:
                    self.Refresh()
                    self.RefreshBot()
                else:
                    rmsg = self.UserName + ": " + msg.decode() + "\n"
                    mine = "You: " + msg.decode() + "\n"
                    self.Mainwin.addstr(mine ,self.MainColor)
                    self.Send(self.Encrypt(rmsg))
                    self.Refresh()
                    self.RefreshBot()

    def HandleKeys(self):
        secret = self.GetEncKeys()
        pyDict = self.Load(secret)
        self.KEY = b64decode(pyDict["KEY"])
        self.IV  = b64decode(pyDict["IV"])

    def InitInfo(self):
        info = self.GetInfo()
        self.CreTime = info["CT"]
        self.OnlineUsers = info["OU"]
        
    def ScrollWithKeys(self):
        cmd = self.Mainwin.getch()
        position = self.ps
        if cmd == KEY_DOWN:
            position += 1
            self.ps   = position
        elif cmd == KEY_UP:
            position -= 1
            self.ps   = position

        self.Mainwin.refresh(position , 0 , 2 , 0 , (Termh - 2), Termw)


    def RefreshTop(self):
        self.Topwin.erase()
        self.Topwin.addstr(" Creation Time: {}         Online Users: ".format(self.CreTime) , self.MainColor | A_BOLD)
        self.Topwin.addstr(str(self.OnlineUsers) + "\n" , GREEN | A_BOLD)
        h , width = self.Topwin.getmaxyx()
        bord = "¯" * (width - 2)
        self.Topwin.addstr(bord , self.MainColor | A_BOLD)
        self.Topwin.refresh()

    def RefreshBot(self):
        self.Botwin.erase()
        self.Botwin.addstr("[{}] 》".format(self.UserName)  , self.MainColor)
        self.Botwin.refresh()

    def Refresh(self):
        position = self.offset
        y , x = self.Mainwin.getyx()
        
        if y > (Termh - 4):
            position   += 1
            self.offset = position

        self.Mainwin.refresh(position , 0 , 2 , 0 , (Termh - 2), Termw)


    def Encrypt(self , msg):
        obj = AES.new(self.KEY , AES.MODE_CFB , self.IV)
        bits = obj.encrypt(msg.encode())

        encrypted = b64encode(bits)

        return encrypted.decode()

    def Decrypt(self , msg):
        obj = AES.new(self.KEY , AES.MODE_CFB , self.IV)
        bits = b64decode(msg)

        decrypted = obj.decrypt(bits)

        return decrypted


    def ChangeColor(self , cmd):
        try:
            parts = (cmd.decode()).split(" ")
            target = parts[1]
            color  = parts[2]

            if color == "red" or color == "1":
                acolor = color_pair(1)

            elif color == "green" or color == "2":
                acolor = color_pair(2)

            elif color == "yellow" or color == "3":
                acolor = color_pair(3)

            elif color == "blue" or color == "4":
                acolor = color_pair(4)

            elif color == "cyan" or color == "5":
                acolor = color_pair(5)

            elif color == "magenta" or color == "6":
                acolor = color_pair(6)

            elif color == "white" or color == "7":
                acolor = color_pair(7)

            elif color == "black" or color == "8":
                acolor = color_pair(8)

            if target == "r":
                self.MsgColor = acolor
            elif target == "m":
                self.MainColor = acolor
            else:
                self.ColorHelpPage()
        except:
            self.ColorHelpPage()


    def ClearScreen(self):
        self.Mainwin.erase()
        self.offset = 0
        self.Refresh()

    def HelpPage(self):
        header = "Welcome in our Room\n"
        page = """Help Menu:
    /color   : Change color.
    /clear   : Clear the screen.
    /help    : Show this page.
    /exit    : Exit program safely.
"""
        self.Mainwin.addstr(header ,self.MainColor | A_BOLD)
        self.Mainwin.addstr(page ,self.MainColor)
        self.Refresh()

    def ColorHelpPage(self):
        output = """USAGE:
    /color [OPTION] [COLOR]
    use /color with option and the name or the number of the color from the table below...
        1 : red                r : received messages
        2 : green              m : main color
        3 : yellow
        4 : blue
        5 : cyan
        6 : magenta
        7 : white
        8 : black
"""
        self.Mainwin.addstr(output , self.MainColor)
        self.Refresh()






screen = initscr()
def Config(screen):
    global Termh , Termw , topw , mainw, botw , RED , YELLOW , GREEN
    Termh , Termw = screen.getmaxyx()
    if Termw < 120:
        screen.addstr("Please run the program in a full screen terminal. Press Enter to exit")
        screen.getch()
        sleep(0.2)
        exit()
   
    topw  = newwin(2 , Termw , 0 , 0)
    mainw = newpad(1000 , Termw)
    botw  = newwin(1 , Termw , (Termh - 1) , 0)

    echo()

    Textbox(botw)
    use_default_colors()

    use_default_colors()
    init_pair(1 , COLOR_RED , -1)
    init_pair(2 , COLOR_GREEN , -1)
    init_pair(3 , COLOR_YELLOW , -1)
    init_pair(4 , COLOR_BLUE , -1)
    init_pair(5 , COLOR_CYAN , -1)
    init_pair(6 , COLOR_MAGENTA , -1)
    init_pair(7 , COLOR_WHITE , -1)
    init_pair(8 , COLOR_BLACK , -1)

    RED     = color_pair(1)
    GREEN   = color_pair(2)
    YELLOW  = color_pair(3)
    BLUE    = color_pair(4)
    CYAN    = color_pair(5)
    MAGENTA = color_pair(6)
    WHITE   = color_pair(7)
    BLACK   = color_pair(8)


    ui = UI()


wrapper(Config)

