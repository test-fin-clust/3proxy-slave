import yaml
import sys
import asyncio
from UserController import User, UserFile, DBConnect
from InfoServer import Serv_info, ConfigInfo
from ShellConect import WSConect
import threading

# Path to file 
cfg_info: ConfigInfo = None
usr_file: UserFile = None
db_conn: DBConnect = None
ws_shel: WSConect = None

def check_ini_cfg_file(path: str)-> bool:
    global usr_file, cfg_info, db_conn, ws_shel
    with open(path,'r', encoding="utf-8") as f:
        confg = yaml.safe_load(f)
        info = Serv_info(name=confg['name'], ip=confg['ip'], maxcon=confg['maxcon'])
        cfg_info = ConfigInfo.init(confg['3proxy']['config'], info)
        usr_file = UserFile.init(confg['3proxy']['users'])
        db_conn = DBConnect.init(pth= confg['bd'])
        ws_shel = WSConect.config(confg['endpoint'], confg['token'])
        ws_shel.init(cfg_info, db_conn, usr_file)
        f.close()
        return True

    return False

def check_valid_cntrl_obj() -> bool:
    print("Add check valid object runner")

    return ws_shel.isCorrect()

async def main()-> None:
    global usr_file, cfg_info, db_conn, ws_shel
    if not check_valid_cntrl_obj():
        print("Object is'nt checker object")
        return
    
    print(f"Debug INFO of object: {usr_file}, {cfg_info.toJsonInfo()}, {db_conn.getAllActiveUser()}, {ws_shel}")
    
    await ws_shel.connect()

##TODO change to mutex
    while ws_shel.canWork:
        mess = await asyncio.to_thread(input, "Print ~q for exit ")
        if mess == '~q':
            break
        if mess == '/user' or mess == '/u':
            if not ws_shel.isUpdateUsers():
               await ws_shel.listUsers()
            else:
                print( f"{ws_shel.isUpdateUsers()} data {ws_shel.getUsers()}" )
        elif mess == '/bd':
            print(f"All active users in file {db_conn.getAllActiveUser()}")
        if '/' in mess:
            continue
        await ws_shel.send(mess)
    await ws_shel.close()

    ws_shel.canBlock.wait()


if len(sys.argv) > 1:
    if check_ini_cfg_file(sys.argv[1]): 
        asyncio.run(main())
    else: 
        print('file error open')
else:
    print(f'please {sys.argv[0]} [path to cofig file]')
    exit(-1)

    
