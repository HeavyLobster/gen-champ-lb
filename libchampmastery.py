"""A library for looking up champion mastery data."""

__version__ = '0.0a1'
__author__ = 'Heavy Lobster'

import sys
from cassiopeia import baseriotapi
from cassiopeia.type.api import exception


def add_user(key, userData, region, newUsers):
    """Adds user data from the api to a dict."""
    # Raise ValueError if there are more than 40 names to look up
    if len(newUsers) > 40:
        raise ValueError('Only able to handle 40 users at a time')

    # Pre-process arguments
    region = region.lower()

    for username in newUsers:
        newUsers[newUsers.index(username)] = username.lower()

    # Set up baseriotapi
    baseriotapi.set_api_key(key)
    baseriotapi.set_region(region)

    # Get user data
    fetchedUserData = baseriotapi.get_summoners_by_name(newUsers)

    # Initialize an empty dict for the region if one doesn't exist yet
    if region not in userData:
        userData[region] = dict()

    # Iterate over fetched data, filling in information and defaults
    for username in newUsers:
        try:
            userData[region][fetchedUserData[username].id] = {
                'name': fetchedUserData[username].name,
                'mastery': 0,
            }

        except KeyError:
            print(
                'Unable to add data for {0}'.format(username),
                file=sys.stderr
            )

    return userData


def rem_user(userData, region, rmUsers):
    """Removes user data based on usernames."""
    region = region.lower()

    for username in rmUsers:
        rmUsers[rmUsers.index(username)] = username.lower()

    for userId, userInfo in userData.items():
        if userInfo['name'].lower() in rmUsers:
            del userData[region][userId]

    return userData


def update_user_mastery(key, userData, champId):
    """Takes a riot api key and a json of user information and
        returns a list<User>.
    """
    # Set key
    baseriotapi.set_api_key(key)

    # Iterate over regions in user data
    for region in userData:
        baseriotapi.set_region(region)

        # Iterate over user IDs in region data
        for userId, userInfo in userData[region].items():
            try:
                userInfo['mastery'] = baseriotapi.get_champion_mastery(
                    int(userId),
                    champId
                ).championPoints
            except exception.APIError:
                print(
                    'Unable to get user mastery for {0} {1}'.format(region, username),
                    file=sys.stderr
                )

    return userData


def sort_users(userData):
    """Takes a dict and returns a sorted list of dict items."""
    users = []

    for region, regionUsers in userData.items():
        for userId, userInfo in regionUsers.items():
            userDict = {
                'id': userId,
                'region': region,
                'name': userInfo['name'],
                'mastery': userInfo['mastery'],
            }
            users.append(userDict)

    return sorted(users, key=lambda user: int(user['mastery']), reverse=True)
