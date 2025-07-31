from datetime import datetime, date, time, timedelta
from dataclasses import dataclass
from typing import TextIO, List
import sqlite3

@dataclass
class User:
    login: str
    password: str
    upDate: datetime = None

    def isActive(self) -> bool:
        if self.upDate is None:
            return False 
        return datetime.now() < self.upDate
    
    @classmethod
    def parse(cls, data: str): 
        sp_d = data.split(':CL:')
        if len(sp_d) > 1:
            return cls(
                login = sp_d[0],
                password = sp_d[1]
            )
        sp_d = data.split('@')
        if len(sp_d) > 2:
            return cls(
                login = sp_d[0],
                password = sp_d[1],
                upDate = datetime.fromisoformat(sp_d[2])
            )

    def toLine(self) -> str:
        return f"{self.login}:CL:{self.password}\n"
    
    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.login == other.login #and self.password == other.password

    
@dataclass
class UserFile:
    path: str = ""
    file: TextIO | None = None
    usr_list: List[User] = None

    @classmethod
    def init(cls, path: str):
        try:
            fil = open(path, 'r+', encoding="utf-8")
            return cls(path=path, file=fil, usr_list = list())
        except IOError:
            return cls(path=path, usr_list = list()) 

    def close(self):
        if self.file is None:
            return
        self.file.close() 

    def isValid(self) -> bool:
        if self.file is None:
            return False
        return not self.file.closed

    def read_allUser(self):
        if not self.isValid():
            return None
        self.file.seek(0)
        spl_rwtxt = self.file.read().split("\n")
        self.usr_list.clear()
        for s in spl_rwtxt:
            self.usr_list.append(User.parse(s))
        return self.usr_list

    def reWriteAllUser(self):
        file = self.file
        file.seek(0)
        for usr in self.usr_list:
            if usr is not None:
                file.write(usr.toLine())
        file.truncate()
    
    def isContainUser(self, usr :User) -> bool:
        return usr in self.usr_list
    
    def addUser(self, usr :User): 
        if (self.isContainUser(usr)):
            self.usr_list.remove(usr)
        self.usr_list.append(usr)
    
    def delUser(self, usr :User): 
        if (self.isContainUser(usr)):
            self.usr_list.remove(usr)

@dataclass
class DBConnect: 
    path: str = "" 
    conn: sqlite3.Connection = None

    @classmethod
    def init(cls, pth: str):
        return cls(
            path = pth,
            conn = sqlite3.connect(pth)
        )
    
    def isValid(self)-> bool: 
        return self.conn is not None
    
    def close(self): 
        self.conn.close()
    
    def sendSimple(self, query: str, params: tuple = ()):
        if (self.isValid()):
            self.conn.cursor().execute(query, params)
            self.conn.commit()

    def addNewUser(self, usr: User):
        self.sendSimple(f"INSERT INTO users (login, password, toDate) VALUES (?, ?, ?)", (usr.login, usr.password, usr.upDate))

    def getOnLogin(self, login: str) -> User:
        curs = self.conn.cursor()
        curs.execute("SELECT login, password, toDate FROM users WHERE login = ?", (login,))
        row = curs.fetchone()
        if row:
            return User(login=row[0],password=row[1], upDate=datetime.fromisoformat(row[2]) if row[2] else None)
        return None

    def getAllActiveUser(self) -> list[User]:
        curs = self.conn.cursor()
        curs.execute("SELECT login, password, toDate FROM users WHERE toDate IS NULL OR toDate > datetime('now')")
        return [
            User(
                login = row[0],
                password=row[1],
                upDate=datetime.fromisoformat(row[2]) if row[2] else None
            )
            for row in curs.fetchall()
        ]

    def delUser(self, login: str):
        curs = self.conn.cursor()
        curs.execute("DELETE FROM users WHERE login = ?", (login,))
        row = curs.fetchone()
        if row:
            return User(login=row[0],password=row[1], upDate=datetime.fromisoformat(row[2]) if row[2] else None)
        return None

    def remove_all_unactive(self):
        self.sendSimple("DELETE FROM users WHERE toDate IS NULL OR toDate < datetime('now')")
    
    def isContain(self, login: str) -> bool:
        curs = self.conn.cursor()
        curs.execute("SELECT login, password, toDate FROM users WHERE login = ?", (login,))
        row = curs.fetchone()
        if row:
            return True
        return False
    
    def updateUser(self, usr: User):
        self.sendSimple(f"UPDATE users SET password = ?, upDate = ? WHERE login = ?", (usr.login, usr.password, usr.upDate))
