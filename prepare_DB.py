import os
import sqlite3
from sqlite3 import Error

main_path = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(main_path,"steam_stats.db")

#create database
try:
    conn = sqlite3.connect(db_path)
except Error:
    print(Error)
cursor = conn.cursor()

#create steam_stats table
q = """
create table if not exists steam_stats
(
    refresh_date text,
    game text,
    current_players integer,
    peak_today integer,
    PRIMARY KEY (refresh_date, game)
)
"""


cursor.execute(q)
conn.commit()

#create table with token and expiration date
q ="""
create table if not exists twitch_token
(
token text PRIMARY KEY,
expiration_date text
)
""" 
cursor.execute(q)
conn.commit()


# steam_twitch_mapping
q ="""
create table if not exists steam_twitch_mapping
(
steam_game text PRIMARY KEY,
twitch_game text,
twitch_game_id int
)
""" 
cursor.execute(q)
conn.commit()

# twitch_game_info
q ="""
create table if not exists twitch_game_info
(
twitch_id int PRIMARY KEY,
release_date,
num_expansions int,
num_dlcs int 
)
""" 
cursor.execute(q)
conn.commit()

#twitch_game_involved_companies
q ="""
create table if not exists twitch_game_involved_companies
(
twitch_id int,
company_id,
role text,
PRIMARY KEY(twitch_id,company_id,role)
)
""" 
cursor.execute(q)
conn.commit()

#twitch_game_genres
q ="""
create table if not exists twitch_game_genres
(
twitch_id int,
genre_id int,
PRIMARY KEY(twitch_id,genre_id)
)
""" 
cursor.execute(q)
conn.commit()

#twitch_genres
q ="""
create table if not exists twitch_genres
(
genre_id int PRIMARY KEY,
genre_name text
)
""" 
cursor.execute(q)
conn.commit()

#twitch_company
q ="""
create table if not exists twitch_companies
(
company_id int PRIMARY KEY,
company_name text
)
""" 
cursor.execute(q)
conn.commit()

q ="""
create table if not exists runs
(
steam_refresh_date text,
run_datetime text
)
""" 
cursor.execute(q)
conn.commit()

conn.close()