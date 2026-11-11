




import sqlite3
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
db_path = DATA_DIR / "meeting_Program.db"

try:
    conn_db = sqlite3.connect(db_path)
    print('DB 연결')
except:
    print("DB 연결 안 됨")


def MEETINGS_TABLE():
    try:    
        db_path.excute("""
        CREATE TABLE MEETINGS(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100)
        )
        """)
    except:
        print('테이블 이미 있음 ')


db_path.excute("""
CREATE TABLE MEMBERS(
    id INTEGER FOREIGN KEY id REFERENCES MEETINGS,
    name VARCHAR(30)
)
""")

db_path.excute("""
CREATE TABLE RECORDS(
    record TEXT
    id INTEGER FOREIGN KEY id REFERENCES MEETINGS,
    name VARCHAR(50) FOREIGN KEY name REFERNCES MEMBERS
)
""")