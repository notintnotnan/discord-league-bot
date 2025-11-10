import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

try:
    conn = psycopg2.connect(
        dbname=os.environ['RENDER_DATABASE_NAME'],
        user=os.environ['RENDER_DATABASE_USER'],
        password=os.environ['RENDER_DATABASE_PASSWORD'],
        host=os.environ['RENDER_DATABASE_HOST'],
        port=os.environ['RENDER_DATABASE_PORT'],
        sslmode='require'
    )
except Exception as e:
    print(f"Error connecting to database: {e}")

query = '''
CREATE TABLE DISCORD_BOT_LEAGUE(
    PUUID varchar(78) PRIMARY KEY,
    CREATED_AT date NOT NULL,
    DELETED_AT date, 
    FLEX_DIVISION varchar(20),
    FLEX_RANK int,
    SOLO_DIVISION varchar(20),
    SOLO_RANK int
)
'''

try:
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()
except Exception as e:
    if cur:
        cur.close()
    conn.close()
    print(f"Error encountered while creating the table: {e}")