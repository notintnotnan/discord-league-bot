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

try:
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE DISCORD_BOT_LEAGUE(
        PUUID varchar(78) PRIMARY KEY,
        CREATED_AT date NOT NULL,
        DELETED_AT date, 
        FLEX_DIVISION varchar(20),
        FLEX_RANK int,
        FLEX_POINTS int,
        SOLO_DIVISION varchar(20),
        SOLO_RANK int,
        SOLO_POINTS int,
        UPDATED_AT timestamp
    )
    '''
    )
    conn.commit()
    cur.execute('''
    CREATE TABLE DISCORD_BOT_LEAGUE_PHRASES(
        ID SERIAL PRIMARY KEY,
        SENTIMENT boolean NOT NULL,
        PHRASE varchar NOT NULL
    )
    ''')
    conn.commit()
except Exception as e:
    if cur:
        cur.close()
    conn.close()
    print(f"Error encountered while creating the table: {e}")

try:
    cur.execute('''
    CREATE TABLE DISCORD_BOT_LEAGUE_PHRASES(
        ID SERIAL PRIMARY KEY,
        SENTIMENT boolean NOT NULL,
        PHRASE varchar NOT NULL
    )
    ''')
    conn.commit()
    with open('../media/phrases.txt', encoding='utf-8') as phrases:
        for line in phrases.readlines():
            sentiment, phrase = line.split(';')
            cur.execute('''
            INSERT INTO DISCORD_BOT_LEAGUE_PHRASES (
                SENTIMENT,
                PHRASE            
            ) VALUES (
                %s,
                %s
            )
            ''',(sentiment, phrase))
            conn.commit()
    
except Exception as e:
    cur.close()
    conn.close()
    print(f"Error encountered while creating the table: {e}")

if cur:
    cur.close()
    conn.close()