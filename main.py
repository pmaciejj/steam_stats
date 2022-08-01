import os
import shutil
import requests
import datetime
from bs4 import BeautifulSoup

import db_op
import twitch_api
from config import db_path
steam_stats_url = r"https://store.steampowered.com/stats/"

with requests.session() as s:
    req = s.get(steam_stats_url)
    if req.status_code == 200:
        stat = req.text


soup = BeautifulSoup(stat, "html.parser")

# get update date string and convert into to datetime
update_date = soup.find("span",class_ = "statsTopSmall secondary_text").text
update_date = update_date.replace("Updated: ","").replace("@ ","")
update_date_dt = datetime.datetime.strptime(update_date,"%d %B, %Y %I:%M%p")
update_date_dt = update_date_dt.strftime("%Y-%m-%d %H:%M:%S")


# get table of stats as list of list
stats = []

stat_table = soup.find("div", id = "detailStats").find("table")
tab_rows = stat_table.findAll("tr")

for i,r in enumerate(tab_rows):
    r_cols = r.findAll("td")
    cols = [ c.text.replace("\n","") for c in r_cols if len(c.text) > 2]
    if i > 1:
        cols[0] = int(cols[0].replace(",",""))
        cols[1] = int(cols[1].replace(",",""))
        stats.append(cols)

# prepare list of tuples for insert into stats table in db (refresh_date,game,current,peak)
rows =[]
for s in stats:
    rows.append((update_date_dt,s[2],s[0],s[1]))

db_op.steam_stats_insert(rows)
db_op.runs_insert(update_date_dt)

if db_op.twitch_get_active_token() is None:
    t_exdate = twitch_api.token_get()
    db_op.twitch_token_insert(t_exdate[0],t_exdate[1])
    twitch_api.token = t_exdate[0]
else:
    twitch_api.token = db_op.twitch_get_active_token()


games = db_op.missing_games_get()

for game in games:
    if db_op.steam_twitch_mapping_check(game) == 0:
        print(game)
        game_info = twitch_api.game_info_get(game = game)
        if len(game_info) ==0:
            continue
        game_info = game_info[0]

        if "parent_game" in game_info.keys():
            game_info = twitch_api.game_info_get(id = game_info["parent_game"])
            game_info = game_info[0]
        elif "version_parent" in game_info.keys():
            game_info = twitch_api.game_info_get(id = game_info["version_parent"])
            game_info = game_info[0]

        twitch_game_id = game_info["id"]
        twitch_game = game_info["name"]

        db_op.steam_twitch_mapping_insert(game,twitch_game,twitch_game_id)
        if "first_release_date" in game_info.keys():
            release_date = datetime.datetime.fromtimestamp(game_info["first_release_date"]).strftime("%Y-%m-%d")
        else:
            release_date = None
        if "expansions" in game_info.keys():
            num_expansions = len(game_info["expansions"])
        else:
            num_expansions = None
        if "dlcs" in game_info.keys():
            num_dlc = len(game_info["dlcs"])
        else:
            num_dlc = None
        db_op.twitch_game_info_insert(twitch_game_id,release_date,num_expansions,num_dlc)

        involved_companies = twitch_api.involved_companies_get(twitch_game_id)
        inv_comp_data = []
        for ic in involved_companies:
            company_id = ic["company"]
            for k,v in ic.items():
                if v == True:
                    role = k
                    if ic["id"] != 134846: #terraria same company twice as publisher
                        inv_comp_data.append((twitch_game_id,company_id,role))

        db_op.twitch_game_involved_companies_insert(inv_comp_data)
        if "genres" in game_info.keys():
            genres = game_info["genres"]
            game_genres = [ (twitch_game_id,g) for g in genres]
            db_op.twitch_game_genre_insert(game_genres)

companies = db_op.missing_companies_get()
if len(companies)>0:
    for comp in companies:
        comp_data = twitch_api.company_get(comp)[0]
        db_op.twitch_companies_insert(comp_data["id"],comp_data["name"])

if db_op.missing_genres_check() > 0:
    genres = twitch_api.genres_get()
    genres_data = [tuple(g.values()) for g in genres]
    db_op.twitch_genres_insert(genres_data)

db_op.conn_close()


#create db copy without token data
# db_path_copy = db_path.replace(".db","_without_token.db")
# if os.path.isdir(db_path_copy):
#     os.remove(db_path_copy)

# shutil.copy(db_path,db_path_copy)
# db_op.token_clear(db_path_copy)
