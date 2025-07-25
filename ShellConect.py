import websockets
import asyncio
from dataclasses import dataclass

@dataclass
class WSConect: 
    token: str = ""
    server: str = "ws://localhost:8080/ws?token="

    @classmethod
    def config(cls, token: str):
        return cls (
            token = token
        )
    
    async def handler_messages(self, ws):
        try:
            async for ms in ws: 
                print(f"[server] {ms}")
        except websockets.exceptions.ConnectionClosed:
            print(f"[s:err] Connection close")
        print("exit")

    async def connect(self):
        url = self.server + self.token
        async with websockets.connect(url) as ws: 
            handler_tsk = asyncio.create_task(self.handler_messages(ws))
            while True:
                message = input("[client] input:")
                if message == "~q":
                    break
                await ws.send(message)
            print("[END]")

tkn = "4b3c24f9fdca46bc8a0b94b3a747045e" 

wscon = WSConect.config(tkn)
asyncio.run(wscon.connect())