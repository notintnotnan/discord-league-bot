import os
import psycopg2
import datetime

from dotenv import load_dotenv

def translate_rank(rank):
    match rank:
        case "IV":
            return 4
        case "III":
            return 3
        case "II":
            return 2
        case "I":
            return 1

def add_player(puuid, flex_division, flex_rank, solo_division, solo_rank):
    try:
        conn = psycopg2.connect(
            dbname=os.environ['RENDER_DATABASE_NAME'],
            user=os.environ['RENDER_DATABASE_USER'],
            password=os.environ['RENDER_DATABASE_PASSWORD'],
            host=os.environ['RENDER_DATABASE_HOST'],
            port=os.environ['RENDER_DATABASE_PORT'],
            sslmode='require'
        )
        cur = conn.cursor()
    except:
        raise psycopg2.DatabaseError

    try:
        query = '''
        INSERT INTO DISCORD_BOT_LEAGUE (
            PUUID,
            CREATED_AT,
            DELETED_AT,
            FLEX_DIVISION,
            FLEX_RANK,
            SOLO_DIVISION,
            SOLO_RANK
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        '''
        data_to_insert = (puuid,datetime.date.today(),None,flex_division,translate_rank(flex_rank),solo_division,translate_rank(solo_rank))
        cur.execute(query,data_to_insert)
        conn.commit()
        cur.close()
        conn.close()
    except:
        raise psycopg2.DatabaseError