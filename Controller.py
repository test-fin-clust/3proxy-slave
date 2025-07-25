import yaml
import sys
from UserController import User, UserFile, DBConnect
from InfoServer import Serv_info, ConfigInfo

# Path to file 
cfg_info: ConfigInfo = None
usr_file: UserFile = None
db_conn: DBConnect = None

def check_ini_cfg_file(path: str):
    global usr_file, cfg_info, db_conn
    with open(path,'r', encoding="utf-8") as f:
        confg = yaml.safe_load(f)
        info = Serv_info(name=confg['name'], ip=confg['ip'], maxcon=confg['maxcon'])
        cfg_info = ConfigInfo.init(confg['3proxy']['config'], info)
        usr_file = UserFile.init(confg['3proxy']['users'])
        db_conn = DBConnect.init(pth= confg['bd'])
        f.close()
        return True

    return False

def main():
    print(f"info: {usr_file}, {cfg_info.toJsonInfo()}, {db_conn.getAllActiveUser()}")


if len(sys.argv) > 1:
    if check_ini_cfg_file(sys.argv[1]): 
        main()
    else: 
        print('file error open')
else:
    print(f'please {sys.argv[0]} [path to cofig file]')
    exit(-1)

    
