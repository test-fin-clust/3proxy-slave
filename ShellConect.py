import websockets
import asyncio
from dataclasses import dataclass

@dataclass
class WSConect: 
    token: str = ""
    server: str = "ws://localhost:8080/ws?token="
    ws = None
    handler = None


    def isValid(self) -> bool: 
        return self.ws is not None and self.handler is not None

    @classmethod
    def config(cls, token: str):
        return cls (
            token = token
        )
    
    async def handler_messages(self):
        print(":run")
        try:
            async for ms in self.ws: 
                print(f"[server] {ms}")
        except websockets.exceptions.ConnectionClosed:
            print(f"[s:err] Connection close")
        print("exit")

    async def connect(self):
        url = self.server + self.token
        self.ws = await websockets.connect(url)
        self.handler = asyncio.create_task(self.handler_messages())
        

    async def send(self, msg: str):
        if (self.isValid()):
            await self.ws.send(msg)
        else: 
            print("[connect] Not Valid")
    
    async def listUsers(self):
        await self.send("~users simple")



    async def close(self):
        if self.ws != None:
            await self.ws.close()
        if self.handler != None:
            self.handler.cancel()


async def main():
    tkn = "4b3c24f9fdca46bc8a0b94b3a747045e" 
    wscon = WSConect.config(tkn)

    await wscon.connect()
    await wscon.listUsers()

    await wscon.send("~test")

    await wscon.close()

asyncio.run(main())