from dotenv import load_dotenv
import os
import oracledb

load_dotenv() #load the env stuff 

user = os.getenv("ORACLE_USER")
password = os.getenv("ORACLE_PASSWORD")
dsn = os.getenv("ORACLE_DSN")

con = oracledb.connect(user=user, password=password, dsn=dsn)

cur = con.cursor()


def addGame(gameName):
    
    cur.execute()

cur.execute("SELECT * FROM test")
for row in cur:
    print(row)
cur.close()
