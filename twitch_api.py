import requests
import json
import datetime
from time import sleep

from config import twitch_client_id
from config import twitch_client_secret


auth_url = "https://id.twitch.tv/oauth2/token"
igdb_url = "https://api.igdb.com/v4/"

s = requests.session()

def token_get() ->list:

    global token
    global expiration_date

    params ={
        "client_id": twitch_client_id,
        "client_secret": twitch_client_secret,
        "grant_type":"client_credentials"
    }


    ts = datetime.datetime.now().replace(microsecond=0)
    
    req = s.post(auth_url,params=params)
    if req.status_code == 200:
        res = json.loads(req.text)
        token = res["access_token"]
        expiration_date = ts + datetime.timedelta(seconds=int(res["expires_in"]))

        return [token,expiration_date]
    else:
        print(req.status_code)
        print(req.text)

def game_info_get(game="",id=0) ->list:

    url = igdb_url + "games"

    header ={
        "Client-ID": twitch_client_id,
        "Authorization": "Bearer " + token 
    }
    if len(game)>1 and id ==0:
        data = "fields *;search" + '"'+ game + '"'  +";"
    elif game == "" and id != 0:
        data = "fields *;where id=" + str(id) + ";"
    sleep(1)
    req = s.post(url,data=data.encode('utf-8'),headers=header)
    if req.status_code == 200:
        res = json.loads(req.text)
        return res
    else:
        print(req.status_code)
        print(req.text)

def involved_companies_get(twitch_game_id:int) ->list:


    url = igdb_url + "involved_companies"
    header = {
        "Client-ID": twitch_client_id,
        "Authorization": "Bearer " + token
    }

    data = "fields *;where game = " + str(twitch_game_id)  + ";"
    sleep(1)
    req = s.post(url,data=data,headers=header)
    if req.status_code == 200:
        res = json.loads(req.text)
        return res
    else:
        print(req.status_code)
        print(req.text)

def genres_get()->list:

    url = igdb_url + "genres"

    header = {
        "Client-ID": twitch_client_id,
        "Authorization": "Bearer " + token
    }

    data = "fields id,name;limit 500;"
    sleep(1)
    req = s.post(url,data=data,headers=header)
    if req.status_code == 200:
        res = json.loads(req.text)
        return res
    else:
        print(req.status_code)
        print(req.text)

def company_get(company_id:int)->list:

    url = igdb_url + "companies"

    header = {
        "Client-ID": twitch_client_id,
        "Authorization": "Bearer " + token
    }

    data = "fields id,name;where id =" + str(company_id) + ";"
    sleep(1)
    req = s.post(url,data=data,headers=header)
    if req.status_code == 200:
        res = json.loads(req.text)
        return res
    else:
        print(req.status_code)
        print(req.text)
