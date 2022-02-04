#!/usr/bin/python3

import socket
from base64 import b64decode , b64encode
from json import dumps, loads
from time import asctime
from Crypto.Random import get_random_bytes
from threading import Thread



class Cipher():
    KEY  = None
    IV   = None

    def GenerateSecret(self):
        bits      = get_random_bytes(32)        
        self.KEY  = (b64encode(bits)).decode() 
        bits2     = get_random_bytes(16)       
        self.IV   = (b64encode(bits2)).decode() 

    def InitSecret(self):                     
                                                
        pyDict = {
            "KEY":self.KEY,
            "IV": self.IV
        }
        json_form = dumps(pyDict)          
        return b64encode((json_form.encode()))


class Server(Cipher):

    IP      = ""
    PORT    = 1235
    Sock    = None

    Clients = {}
    
    Secret  = None
 
    OnlineUsers     = 0
    CreTime         = asctime()

    def __init__(self):
        self.Sock = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
        self.Sock.bind((self.IP , self.PORT))
        self.GenerateSecret()

        self.Sock.listen()
        self.Accpet()

    def Accpet(self):
        while 1:
            connection , addr = self.Sock.accept()
            self.Add(connection)
    
    def Add(self , connection):
        t2 = Thread(target=self.Start , args=[connection]).start()

    def Start(self , connection):
        while 1:
            try:
                Req = connection.recv(1024)
                self.HandleReq(connection , Req)
            except:
                pass

    def HandleReq(self, client , eReq):
        Req = self.Load(eReq)
        print(Req)
        if Req["TYPE"] == "CHECKUSERNAME":
            self.CheckUserName(Req["USERNAME"] , client)
        elif Req["TYPE"] == "CHECKEXIST":
            self.CheckExist(client , Req["USERNAME"])
        elif Req["TYPE"] == "GETENCKEYS":
            self.ProvideKeys(client)
        elif Req["TYPE"] == "INFORMATION":
            self.ProvideInfo(client)
        elif Req["TYPE"] == "MESSAGE":
            if Req["TO"] == "BROADCAST":
                self.BroadCastEx(client , Req["MSG"])
        elif Req["TYPE"] == "JOIN":
            self.JoinMsg(client , Req["NAME"])      
        elif Req["TYPE"] == "EXIT":
            self.ExitMsg(client , Req["NAME"])



    def BroadCastEx(self , client , msg):
        for conn in self.Clients.values():
            if conn == client:
                pass
            else:
                conn.send(msg.encode())
           
    def JoinMsg(self , conn , name):
        body = ">>> " + name + " JOINED!\n"
        self.BroadCastEx(conn , body)

    def ExitMsg(self , conn , name):
        body = "<<< " + name + " EXITED!\n"
        self.BroadCastEx(conn , body)
        self.DelUser(name)

    def DelUser(self , username):
        del self.Clients[username]
        self.ProvideInfo()

    def CheckExist(self , client , name):
        if name in self.Clients:
            Exist = "TRUE"
        else:
            Exist = "FALSE"
        Res = {"TYPE" : "CHECKEXIST" , "RES" : Exist}
        eRes = self.Dump(Res)
        client.send(eRes)

    def CheckUserName(self , username , client):
        if username in self.Clients.keys():
            Res = {"TYPE" : "CHECKUSERNAME" , "RES" : "TRUE"}
            eRes = self.Dump(Res)
            client.send(eRes)
        else:
            Res = {"TYPE" : "CHECKUSERNAME" , "RES" : "FALSE"}
            eRes = self.Dump(Res)
            client.send(eRes)
            self.AddNewUser(username , client)


    def ProvideKeys(self , client):
        self.Secret = self.InitSecret()
        
        Res = {"TYPE" : "KEY" , "SECRET" : str((self.Secret).decode())}
        eRes = self.Dump(Res)
        client.send(eRes)


    def ProvideInfo(self , client):
        self.OnlineUsers = len(self.Clients)
        Res = {"TYPE" : "INFORMATION" , "OU" : self.OnlineUsers , "CT" : self.CreTime}
        eRes = self.Dump(Res)
        client.send(eRes)


    def AddNewUser(self , name , conn):
        self.Clients[name] = conn


    def Load(self , Req):
        JsonForm = b64decode(Req)
        PyDict   = loads(JsonForm)
        return PyDict

    def Dump(self , Req):
        JsonForm = dumps(Req)
        BaseEn   = b64encode(JsonForm.encode())
        return BaseEn
 




s = Server()