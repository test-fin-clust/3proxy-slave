import websockets
import asyncio
from dataclasses import dataclass
from UserController import User

@dataclass
class WSConect: 
    token: str = ""
    server: str = "ws://localhost:8080/ws?token="
    ws = None
    handler = None

    usr_list: list[User] = None
    
    async def handler_messages(self):
        print(":run")
        try:
            async for ms in self.ws: 
                print(f"[server] {ms}")
                if ms.startswith("~"):
                    self.command_parser(ms)
        except websockets.exceptions.ConnectionClosed:
            print(f"[s:err] Connection close")
        print("exit")

    

    def parseUsers(self, msg: str) -> None:
        self.usr_list = list()
        for sm in msg.split("\n"):
            if sm.startswith('~'):
                continue
            if len(sm.split("@")) > 2:
                self.addUser(User.parse(sm))

    def handlerUpdate(self, msg: str) -> None:
        if len(msg.split(' ')) > 1 and self.isUpdateUsers():
            self.addUser(User.parse(msg.split(' ')[1]))            
        else: 
            asyncio.create_task(self.listUsers())

    

    def command_parser(self, msg: str):
        if '~' in msg: 
            if 'users#' in msg: 
                self.parseUsers(msg)
            if 'update' in msg:
                self.handlerUpdate(msg)

    #Block of utilitar function#
    async def connect(self):
        url = self.server + self.token
        self.ws = await websockets.connect(url)
        self.handler = asyncio.create_task(self.handler_messages())

    def isUpdateUsers(self) -> bool: 
        return self.usr_list is not None

    def addUser(self, usr: User) -> None:
        if usr is not None and self.isUpdateUsers(): 
            if usr not in self.usr_list:
                self.usr_list.append(usr)

    def getUsers(self) -> list[User]:
        return self.usr_list

    async def send(self, msg: str):
        if (self.isValid()):
            await self.ws.send(msg)
        else: 
            print("[connect] Not Valid")
    
    async def listUsers(self):
        self.usr_list = None
        await self.send("~users simple")

    async def close(self):
        if self.ws != None:
            await self.ws.close()
        if self.handler != None:
            self.handler.cancel()

    def isValid(self) -> bool: 
        return self.ws is not None and self.handler is not None

    @classmethod
    def config(cls, srv: str, token: str):
        return cls (
            server = srv,
            token = token
        )

async def main():
    tkn = "4b3c24f9fdca46bc8a0b94b3a747045e" 
    wscon = WSConect.config("ws://localhost:8080/ws?token=", tkn)

    await wscon.connect()
    await wscon.listUsers()
    
    while True: 
        cntmsg = await asyncio.to_thread(input, "Print ~q for exit ")
        if cntmsg == "~q":
            break
        if cntmsg == "/user" or cntmsg == "/":
            print( f"{wscon.isUpdateUsers()} data {wscon.getUsers()}" )

        await wscon.send(cntmsg)

    await wscon.close()
