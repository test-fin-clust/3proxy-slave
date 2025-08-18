import websockets
import asyncio
from dataclasses import dataclass
from UserController import User, DataConnect, DBConnect, UserFile
from InfoServer import ConfigInfo
import threading
from aiocron import crontab

@dataclass
class WSDataPresent:
    cfg_info: ConfigInfo = None
    conn: DataConnect = None

    @classmethod
    def init(cls, info: ConfigInfo):
        return cls(
            cfg_info = info
        )

    def isValid(self) -> bool:
        #check nullable's object 
        if self.cfg_info is None:
            return False
        
        #check case of valid object
        if not self.cfg_info.isValid():
            return False

        return True
    
    def getPresentInfo(self) ->str: 
        return f"~info {self.cfg_info.toJsonInfo()}"

@dataclass
class WSConect: 
    token: str = None
    server: str = None
    ws = None
    handler = None
    task = None

    cntrl: DataConnect = None
    data: WSDataPresent = None
    usr_list: list[User] = None

    #flags:
    canWork: bool = False
    canBlock = threading.Event()
    
    async def handler_messages(self) -> None:
        print(":run")
        try:
            async for ms in self.ws: 
                print(f"[server] {ms}")
                if ms.startswith("~"):
                    self.command_parser(ms)
                    continue
        except websockets.exceptions.ConnectionClosed:
            print(f"[s:err] Connection close")
        print("exit")
    
    async def task_period_update(self) -> None:
        await self.send("~users simple")

    #integrated updates
    def parseUsers(self, msg: str) -> None:
        self.usr_list = list()
        for sm in msg.split("\n"):
            if sm.startswith('~'):
                continue
            if len(sm.split("@")) > 2:
                self.addUser(User.parse(sm))
        
        self.cntrl.updates(self.usr_list)

    #integrated update
    def handlerUpdate(self, msg: str) -> None:
        if len(msg.split(' ')) > 1 and self.isUpdateUsers():
            self.cntrl.update(User.parse(msg.split(' ')[1]))
            self.addUser(User.parse(msg.split(' ')[1]))            
        else: 
            asyncio.create_task(self.listUsers())

    #intgrated info
    def handlerInfo(self) -> None: 
        asyncio.create_task(self.send(self.data.getPresentInfo()))

    #integrated clear
    def handlerRefresh(self) -> None: 
        self.cntrl.clear()
        self.handlerInfo()
        asyncio.create_task(self.listUsers())

    def handlerSecure(self) -> None:
        print("[Secure mod] KILL INSTANCE server handler message")
        self.handler.cancel()

    def handlerReload(self) -> None:
        self.canWork = False

    #integrated block
    def handlerBlock(self) -> None:
        self.canWork = False
        self.canBlock.clear()

        self.cntrl.block()

    def command_parser(self, msg: str) -> bool:
        if '~' in msg: 
            if 'users#' in msg: 
                self.parseUsers(msg)
            elif 'update' in msg:
                self.handlerUpdate(msg)
            elif '~info' == msg:
                self.handlerInfo()
            elif '~refresh' == msg:
                self.handlerRefresh()
            elif '~reload' == msg:
                self.handlerReload()
            elif '~block' == msg:
                self.handlerBlock()
            elif '~secure' == msg:
                self.handlerSecure()

            elif '~not' == msg:
                print(f"COMMAND unenabled: {msg}")
        

    #Block of utilitar function#
    async def connect(self) -> None:
        url = self.server + self.token
        self.ws = await websockets.connect(url)
        self.handler = asyncio.create_task(self.handler_messages())
        self.task = crontab("*/1 * * * *", func= self.task_period_update)
        self.canWork = True
        self.canBlock.set()

    def isUpdateUsers(self) -> bool: 
        return self.usr_list is not None

    def addUser(self, usr: User) -> None:
        if usr is not None and self.isUpdateUsers(): 
            if usr not in self.usr_list:
                self.usr_list.append(usr)

    def getUsers(self) -> list[User]:
        return self.usr_list

    async def send(self, msg: str) -> bool:
        if (self.isValid()):
            await self.ws.send(msg)
            return True
        else: 
            print("[connect] Not Valid")
        return False
    
    async def listUsers(self) -> None:
        self.usr_list = None
        await self.send("~users simple")

    async def close(self) -> None:
        if self.ws != None:
            await self.ws.close()
        if self.handler != None:
            self.handler.cancel()
        if self.task != None:
            self.task.stop()

    def isValid(self) -> bool: 
        return self.ws is not None and self.handler is not None and self.data is not None and self.cntrl is not None

    @classmethod
    def config(cls, srv: str, token: str):
        return cls (
            server = srv,
            token = token
        )

    def init(self, info: ConfigInfo, db: DBConnect, file: UserFile):
        self.data = WSDataPresent.init(info)
        self.cntrl = DataConnect.init(db, file)


    def isCorrect(self) -> bool:
        return self.server is not None and self.token is not None
