import sqlite3
import string
from config import db_path
from datetime import datetime

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
except sqlite3.Error as e:
    print(e)

def conn_close():
    conn.close()


def twitch_token_insert(token,expiration_date):
    cursor.execute("insert into twitch_token values (?,?)",(token,expiration_date))
    conn.commit()
    print("new token inserted")

# return None if there is no active token in db or it will expire within 10 mins
def twitch_get_active_token():
    ts = datetime.now().replace(microsecond=0)
    cursor.execute("select token,expiration_date from twitch_token where expiration_date > (?) order by expiration_date desc limit 1",(ts,))
    row = cursor.fetchone()
    if row is None:
        return None
    elif row is not None:
        ex_date = datetime.strptime(row[1],"%Y-%m-%d %H:%M:%S")
        if (ex_date - ts).total_seconds()/60 < 10: return None
    return row[0]

def steam_stats_insert(rows:list):
    cursor.executemany("insert into steam_stats values (?,?,?,?)",rows)
    conn.commit()

def runs_insert(steam_refresh_date:string):
    cursor.execute("insert into runs values (?,datetime('now','localtime'))",(steam_refresh_date,))
    conn.commit()

def steam_twitch_mapping_check(steam_game):
    cursor.execute("select count(*) from steam_twitch_mapping where steam_game = ?",(steam_game,))
    row = cursor.fetchone()
    return row[0]

def steam_twitch_mapping_insert(steam_game,twitch_game,twitch_game_id):
    cursor.execute("insert into steam_twitch_mapping values (?,?,?)",(steam_game,twitch_game,twitch_game_id))
    conn.commit()

def twitch_game_info_insert(twitch_game_id,release_date,num_expansions,num_dlcs):
    cursor.execute("insert into twitch_game_info values (?,?,?,?)",(twitch_game_id,release_date,num_expansions,num_dlcs))
    conn.commit()

def twitch_game_involved_companies_insert(inv_comp_data:list):
    cursor.executemany("insert into twitch_game_involved_companies_v2 values (?,?,?)",inv_comp_data)
    conn.commit()

def twitch_game_genre_insert(game_genres:list):
    cursor.executemany("insert into twitch_game_genres values (?,?)",game_genres)
    conn.commit()

def twitch_genres_insert(genres_data):
    cursor.execute("delete from twitch_genres")
    conn.commit()
    cursor.executemany("insert into twitch_genres values (?,?)",genres_data)
    conn.commit()

def twitch_companies_insert(company_id,company_name):
    cursor.execute("insert into twitch_companies values (?,?)",(company_id,company_name) )
    conn.commit()

def missing_companies_get()->list:
    q = """SELECT distinct A.company_id
        from twitch_game_involved_companies A
        left join twitch_companies B on A.company_id = B.company_id 
        where B.company_id is null"""
    cursor.execute(q)
    rows = cursor.fetchall()
    return [r[0] for r in rows]

def missing_genres_check()->int:
    q ="""select count(A.genre_id)
        from twitch_game_genres A
        left join twitch_genres B on A.genre_id = B.genre_id
        where B.genre_id is null"""
    cursor.execute(q)
    row = cursor.fetchone()
    return row[0]

def missing_games_get():
    q = """select distinct A.game
        from steam_stats A
        left join steam_twitch_mapping B on A.game = B.steam_game
        where B.twitch_game_id is null
        and A.game <>'Soundpad'
        and A.game <>'Wallpaper Engine'
        """
    cursor.execute(q)
    rows = cursor.fetchall()
    return [r[0] for r in rows]

def token_clear(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("delete from twitch_token")
        conn.commit()
    except sqlite3.Error as e:
        print(e)

# --DROP TABLE tid;
# PRAGMA temp_store = 2; 
# CREATE TEMP TABLE tid(id int);
# INSERT INTO tid VALUES (26128);
# delete from steam_twitch_mapping where twitch_game_id = (select id from tid);
# delete from twitch_game_genres where twitch_id  = (select id from tid);
# delete from twitch_game_info where twitch_id  = (select id from tid);
# delete from twitch_game_involved_companies where twitch_id  = (select id from tid);
# DROP TABLE tid;
