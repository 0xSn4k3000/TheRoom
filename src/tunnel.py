#!/usr/bin/python3


import socket
from base64 import b64decode , b64encode
from json import dumps, loads




class Tunnel():

    IP         = ""
    PORT       = 0
    Connection = None

        

    def ConnectToServer(self):
        self.Connection = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        self.Connection.connect((self.IP , self.PORT))


    def CheckUserName(self , Username):
        Req = {"TYPE" : "CHECKUSERNAME" , "USERNAME" : Username}
        eReq = self.Dump(Req)
        self.Connection.send(eReq)

        eRes = self.Connection.recv(1024)
        Res  = self.Load(eRes)
        
        if Res["TYPE"] == "CHECKUSERNAME":
            if Res["RES"] == "TRUE":
                return True
            elif Res["RES"] == "FALSE":
                return False

    def CheckExist(self , username):
        Req = {"TYPE" : "CHECKEXIST" , "USERNAME" : username}
        eReq = self.Dump(Req)
        self.Connection.send(eReq)

        eRes = self.Connection.recv(1024)
        Res  = self.Load(eRes)
        if Res["TYPE"] == "CHECKEXIST":
            if Res["RES"] == "TRUE":
                return True
            elif Res["RES"] == "FALSE":
                return False

    def GetEncKeys(self):
        Req = {"TYPE" : "GETENCKEYS"}
        eReq = self.Dump(Req)
        self.Connection.send(eReq) 

        eRes = self.Connection.recv(1024)
        Res  = self.Load(eRes)

        if Res["TYPE"] == "KEY":
            return Res["SECRET"]


    def GetInfo(self):
        Req = {"TYPE" : "INFORMATION"}
        eReq = self.Dump(Req)
        self.Connection.send(eReq)

        eRes = self.Connection.recv(1024)
        Res  = self.Load(eRes)
        if Res["TYPE"] == "INFORMATION":
            return Res

    def JoinMsg(self , username):
        Req = {"TYPE" : "JOIN" , "NAME" : username}
        eReq = self.Dump(Req)
        self.Connection.send(eReq)

    def ExitMsg(self , username):
        Req = {"TYPE" : "EXIT" , "NAME" : username}
        eReq = self.Dump(Req)
        self.Connection.send(eReq)


    def Listen(self):
        Res = self.Connection.recv(1048)
        return Res

    def Send(self , msg):
        Req = {"TYPE" : "MESSAGE" , "TO" : "BROADCAST" , "MSG" : msg}
        eReq = self.Dump(Req)
        self.Connection.send(eReq)

    def Load(self , Req):
        JsonForm = b64decode(Req)
        PyDict   = loads(JsonForm)
        return PyDict

    def Dump(self , Req):
        JsonForm = dumps(Req)
        BaseEn   = b64encode(JsonForm.encode())
        return BaseEn

