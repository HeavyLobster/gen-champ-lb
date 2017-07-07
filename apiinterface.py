"""An interface for the League of Legends API."""

__version__ = '0.0a3'
__author__ = 'Heavy Lobster'

import time

import requests


key = ""
_ratelimitWait = 0
_endpoints = {
    "br": "br1",
    "eune": "eun1",
    "euw": "euw1",
    "jp": "jp1",
    "kr": "kr",
    "lan": "la1",
    "las": "la2",
    "na": "na1",
    "oce": "oc1",
    "tr": "tr1",
    "ru": "ru",
    "pbe": "pbe1",
}


def _set_ratelimit(rawCallsMade):
    limits = {
        "1": 20,
        "120": 100,
    }

    callsMade = rawCallsMade.split(",")

    for x in range(len(callsMade)):
        callsMade[x] = callsMade[x].split(":")
        callsMade[x][0] = int(callsMade[x][0])

    for item in callsMade:
        calls = item[0]
        timeframe = item[1]

        if calls >= (limits[timeframe] - 3):
            return int(int(timeframe) / 3) + 1

    return 0


def get_user(region, username):
    global key
    global _ratelimitWait

    if _ratelimitWait != 0:
        print(f"Waiting {_ratelimitWait} seconds because of ratelimits")
        time.sleep(_ratelimitWait)

    region = _endpoints[region]

    authHeader = {"x-riot-token": key}

    response = requests.get(
        f"https://{region}.api.riotgames.com/lol"
        f"/summoner/v3/summoners/by-name/{username}",
        headers=authHeader
    )

    _ratelimitWait = _set_ratelimit(response.headers["x-rate-limit-count"])

    return response.json()


def get_mastery(region, champId, userId):
    global key
    global _ratelimitWait

    if _ratelimitWait != 0:
        print(f"Waiting {_ratelimitWait} seconds because of ratelimits")
        time.sleep(_ratelimitWait)

    region = _endpoints[region]

    authHeader = {"x-riot-token": key}

    response = requests.get(
        f"https://{region}.api.riotgames.com/championmastery/location"
        f"/{region}/player/{userId}/champion/{champId}",
        headers=authHeader
    )

    _ratelimitWait = _set_ratelimit(response.headers["x-rate-limit-count"])

    return response.json()
