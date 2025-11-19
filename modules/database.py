import os
import psycopg2
import datetime
import requests

from psycopg2.errors import UniqueViolation, DataError
from modules.rank import Rank

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

def add_player(puuid, flex_division, flex_rank, flex_points, solo_division, solo_rank, solo_points):
    try:
        conn = psycopg2.connect(
            dbname=os.environ['DATABASE_NAME'],
            user=os.environ['DATABASE_USER'],
            password=os.environ['DATABASE_PASSWORD'],
            host=os.environ['DATABASE_HOST'],
            port=os.environ['DATABASE_PORT'],
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
            FLEX_POINTS,
            SOLO_DIVISION,
            SOLO_RANK,
            SOLO_POINTS,
            UPDATED_AT
        ) VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        '''
        data_to_insert = (
            puuid,
            datetime.date.today(),
            None,
            flex_division,
            translate_rank(flex_rank),
            flex_points,
            solo_division,
            translate_rank(solo_rank),
            solo_points,
            None
        )
        cur.execute(query,data_to_insert)
        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.errors.UniqueViolation:
        UniqueViolation("That player is already registered.")
    
    except:
        if cur:
            cur.close()
        if conn:
            conn.close()
        raise psycopg2.DatabaseError
    
def show_player(playerName, tagLine, riot_token):
    try:
        conn = psycopg2.connect(
            dbname=os.environ['DATABASE_NAME'],
            user=os.environ['DATABASE_USER'],
            password=os.environ['DATABASE_PASSWORD'],
            host=os.environ['DATABASE_HOST'],
            port=os.environ['DATABASE_PORT'],
            sslmode='require'
        )
        cur = conn.cursor()
    except:
        raise ConnectionError("Unable to connect with the database.")
    
    try:
        headers = {
            "X-Riot-Token":riot_token
        }
        response = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{playerName}/{tagLine}",headers=headers)
        player_info = response.json()
        puuid = player_info['puuid']
        
        cur.execute('''
            SELECT FLEX_DIVISION,
                FLEX_RANK,
                FLEX_POINTS,
                SOLO_DIVISION,
                SOLO_RANK,
                SOLO_POINTS
            FROM DISCORD_BOT_LEAGUE
            WHERE
                PUUID = %s
        ''', (puuid,))

        return cur.fetchall()[0]
    except ConnectionError:
        raise ConnectionError("Could not connect to the database.")
    except (KeyError,ValueError):
        raise KeyError("There was an error creating the response.")
    except IndexError:
        raise IndexError("There's no player registred with that name.")
    except Exception:
        raise DataError("There was an error with the database.")

    
def update_player(connection, cursor, player):
    cursor.execute('''
    UPDATE DISCORD_BOT_LEAGUE SET
        FLEX_DIVISION = %s,
        FLEX_RANK = %s,
        FLEX_POINTS = %s,
        SOLO_DIVISION = %s,
        SOLO_RANK = %s,
        SOLO_POINTS = %s,
        UPDATED_AT = %s
    WHERE
        PUUID = %s
    ''',(
            player['flex_tier'],
            player['flex_rank'],
            player['flex_points'],
            player['solo_tier'],
            player['solo_rank'],
            player['solo_points'],
            datetime.datetime.now(),
            player['puuid']
        )
    )
    connection.commit()

def delete_player(playerName, tagLine, riot_token):
    try:
        conn = psycopg2.connect(
            dbname=os.environ['DATABASE_NAME'],
            user=os.environ['DATABASE_USER'],
            password=os.environ['DATABASE_PASSWORD'],
            host=os.environ['DATABASE_HOST'],
            port=os.environ['DATABASE_PORT'],
            sslmode='require'
        )
        cur = conn.cursor()
    except:
        if cur:
            cur.close()
        if conn:
            conn.close()
        raise psycopg2.DatabaseError
    
    try:
        headers = {
            "X-Riot-Token":riot_token
        }
        response = requests.get(f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{playerName}/{tagLine}",headers=headers)
        player_info = response.json()
        puuid = player_info['puuid']

        cur.execute('''
            UPDATE DISCORD_BOT_LEAGUE SET
                DELETED_AT = %s
            WHERE 
                PUUID = %s
        ''',(puuid,))
        conn.commit()
        cur.close()
        conn.close()
        return True

    except:
        cur.close()
        conn.close()
        return False

def update_queues(riot_token):
    
    updates = []

    try:
        conn = psycopg2.connect(
            dbname=os.environ['DATABASE_NAME'],
            user=os.environ['DATABASE_USER'],
            password=os.environ['DATABASE_PASSWORD'],
            host=os.environ['DATABASE_HOST'],
            port=os.environ['DATABASE_PORT'],
            sslmode='require'
        )
        cur = conn.cursor()
    except:
        if cur:
            cur.close()
        if conn:
            conn.close()
        raise psycopg2.DatabaseError
    
    try:
        cur.execute('SELECT * FROM DISCORD_BOT_LEAGUE WHERE DELETED_AT IS NULL')
        players = cur.fetchall()
    except:
        cur.close()
        conn.close()
        raise psycopg2.DatabaseError
    
    for player in players:
        headers = {
            "X-Riot-Token":riot_token
        }
        try:
            url = f"https://la1.api.riotgames.com/lol/league/v4/entries/by-puuid/{player[0]}"
            response = requests.get(url, headers=headers)
            queue_info = response.json()

            flex_data = list(filter(lambda x : 'RANKED_FLEX_SR' in x['queueType'],queue_info))[0]
            solo_data = list(filter(lambda x : 'RANKED_SOLO_5x5' in x['queueType'],queue_info))[0]

            if (
                Rank(flex_data['tier'],translate_rank(flex_data['rank']))!=Rank(player[3],player[4]) or 
                    Rank(solo_data['tier'],translate_rank(solo_data['rank']))!=Rank(player[6],player[7])
                ):
                url = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-puuid/{player[0]}"
                response = requests.get(url, headers=headers)
                player_data = response.json()
                if Rank(flex_data['tier'],translate_rank(flex_data['rank']))!=Rank(player[3],player[4]):
                    updates.append({
                        "name":player_data['gameName'],
                        "tier":flex_data['tier'],
                        "rank":flex_data['rank'],
                        "queue":"FLEX",
                        "up":Rank(flex_data['tier'],translate_rank(flex_data['rank']))>Rank(player[3],player[4])
                    })
                if Rank(solo_data['tier'],translate_rank(solo_data['rank']))!=Rank(player[6],player[7]):
                    updates.append({
                        "name":player_data['gameName'],
                        "tier":solo_data['tier'],
                        "rank":solo_data['rank'],
                        "queue":"SOLO/DUO",
                        "up":Rank(solo_data['tier'],translate_rank(solo_data['rank']))>Rank(player[6],player[7])
                    })
                try:
                    update_player(
                        conn,
                        cur,
                        {
                            "puuid": solo_data['puuid'],
                            "flex_tier":flex_data['tier'],
                            "flex_rank":translate_rank(flex_data['rank']),
                            "flex_points":flex_data['leaguePoints'],
                            "solo_tier":solo_data['tier'],
                            "solo_rank":translate_rank(solo_data['rank']),
                            "solo_points":solo_data['leaguePoints']
                        }
                    )
                except Exception as e:
                    cur.close()
                    conn.close()
                    raise e

        except Exception as e:
            cur.close()
            conn.close()
            continue
    
    return updates

def get_message(sentiment):
    try:
        conn = psycopg2.connect(
            dbname=os.environ['DATABASE_NAME'],
            user=os.environ['DATABASE_USER'],
            password=os.environ['DATABASE_PASSWORD'],
            host=os.environ['DATABASE_HOST'],
            port=os.environ['DATABASE_PORT'],
            sslmode='require'
        )
        cur = conn.cursor()
    except:
        raise psycopg2.DatabaseError
    
    try:
        cur.execute('''
            SELECT PHRASE 
            FROM DISCORD_BOT_LEAGUE_PHRASES
            WHERE SENTIMENT = %s
            ORDER BY RANDOM()
            LIMIT 1
        ''',(sentiment,))
        phrase = cur.fetchall()[0]
        return phrase[0].strip().replace("\\","").replace('"',"")
    except:
        return "Wish I had words to describe the event!"