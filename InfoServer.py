from dataclasses import dataclass
from typing import TextIO
import json

@dataclass
class Serv_info:
    name: str 
    ip: str
    maxcon: int

@dataclass
class ConfigInfo: 
    cfg_px: str = None
    path: str = ""
    info: Serv_info = None

    @classmethod
    def init(cls, pth: str, inf: Serv_info):
        with open(pth, 'r', encoding="utf-8") as f: 
            f.seek(0)
            msg = f.read()
            f.close()
            return cls(
                cfg_px = msg,
                path = pth,
                info = inf
            )
    
    def isValid(self) -> bool:
        return self.cfg_px is not None and self.path != "" and self.info is not None

    def toJsonInfo(self) -> str:
        data = {
            "isValid": self.isValid(),
            "name": self.info.name,
            "ip": self.info.ip,
            "maximal": self.info.maxcon,
            "cofig": self.cfg_px,
            "port": -1
        }
        return json.dumps(data)

    # TODO port and type add implementaion read from file or configure other method's

        