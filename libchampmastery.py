"""A library for looking up champion mastery data."""

__version__ = "0.0a3"
__author__ = "Heavy Lobster"

import sys
import time

import requests


REGIONS = (
    "br", "eune", "euw", "jp", "kr", "lan",
    "las", "na", "oce", "tr", "ru", "pbe"
)


def _parse_ratelimit(rawCallsMade):
    """Parses the ratelimit string returned by the API.

    Args:
        rawCallsMade (string): The "X-Rate-Limit-Count" field from
            the header of responses from the API.

    Returns:
        int: The earliest time another API call may be made.
    """
    # Key is the timeframe, value is the maximum number of requests
    # possible in that timeframe.
    limits = {
        "1": 20,
        "120": 100,
    }

    callsMade = rawCallsMade.split(",")

    # For each pair of values from the API
    for x in range(len(callsMade)):
        # Separate number of calls made from timeframe
        # Index 0: calls made, index 1: timeframe
        callsMade[x] = callsMade[x].split(":")
        callsMade[x][0] = int(callsMade[x][0])

    for item in callsMade:
        calls = item[0]
        timeframe = item[1]

        # If fewer than 4 requests in the timeframe remain,
        # wait 1/4 of the timeframe
        if calls >= (limits[timeframe] - 4):
            waitUntil = time.time() + (int(timeframe) / 4) + 1

            return waitUntil

    return 0


def sort(userData):
    """Sorts the users from a dict into an ordered list.

    Args:
        userData (dict): The user data to work with.

    Returns:
        list<dict>: The user data sorted into a list of dict objects.
    """
    users = []

    # Populate list of users
    for _, userInfo in userData.items():
        users.append(userInfo)

    # Sort list
    users = sorted(
        users,
        key=lambda user: int(user["mastery"]),
        reverse=True
    )

    return users


class ApiInterface():
    """A class for managing keys and ratelimits."""

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

    def __init__(self, key):
        """Sets the key and initializes the ratelimit timers.

        Args:
            key (string): The Riot API key.
        """
        self.key = key
        self.waitUntil = {
            "br": 0,
            "eune": 0,
            "euw": 0,
            "jp": 0,
            "kr": 0,
            "lan": 0,
            "las": 0,
            "na": 0,
            "oce": 0,
            "tr": 0,
            "ru": 0,
            "pbe": 0,
        }


    def user(self, region, username, champId=-1):
        """Fetches user info from the API.

        Args:
            region (string): The region to look in.
            username (string): The user to look for.
        """
        # Pre-process arguments
        region = region.lower()
        username = username.lower().replace(" ", "")

        # Check ratelimit
        if time.time() < self.waitUntil[region]:
            waitTime = self.waitUntil[region] - time.time()
            print(
                f"Waiting {int(waitTime)} seconds "
                "because of ratelimits",
                file=sys.stderr
            )
            time.sleep(waitTime)

        # Make request to the API
        endpoint = ApiInterface._endpoints[region]
        authHeader = {"x-riot-token": self.key}
        response = requests.get(
            f"https://{endpoint}.api.riotgames.com/lol"
            f"/summoner/v3/summoners/by-name/{username}",
            headers=authHeader
        )
        apiData = response.json()

        # Fetch mastery score if requested
        if champId > -1:
            masteryPoints = self.mastery(
                region, champId, apiData["id"]
            )
        # Skip if not
        else:
            masteryPoints = 0

        # Map relevant information to a dict
        userInfo = {
            "id": apiData["id"],
            "region": region,
            "name": apiData["name"],
            "mastery": masteryPoints,
        }

        # Set ratelimit
        self.waitUntil[region] = _parse_ratelimit(
            response.headers["x-app-rate-limit-count"]
        )

        return userInfo


    def mastery(self, region, champId, userId):
        """Fetches a user's mastery score for a champion.

        Args:
            region (string): The region to use.
            champId (int): The ID of the champion.
            userId (int): The ID of the user.

        Returns:
            int: The user's mastery score on the champion.
        """
        # Pre-process arguments
        region = region.lower()

        # Check ratelimit
        if time.time() < self.waitUntil[region]:
            waitTime = self.waitUntil[region] - time.time()
            print(
                f"Waiting {int(waitTime)} seconds "
                "because of ratelimits",
                file=sys.stderr
            )
            time.sleep(waitTime)

        # Make request to the API
        endpoint = ApiInterface._endpoints[region]
        authHeader = {"x-riot-token": self.key}
        response = requests.get(
            f"https://{endpoint}.api.riotgames.com/lol"
            f"/champion-mastery/v3/champion-masteries"
            f"/by-summoner/{userId}/by-champion/{champId}",
            headers=authHeader
        )
        masteryPoints = response.json()["championPoints"]

        # Set ratelimit
        self.waitUntil[region] = _parse_ratelimit(
            response.headers["x-app-rate-limit-count"]
        )

        return masteryPoints
