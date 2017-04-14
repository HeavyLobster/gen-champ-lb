#!/usr/bin/python
"""A library and CLI for looking up champion mastery data."""

__version__ = '0.0a1'
__author__ = 'Heavy Lobster'

import sys
import time
import configparser
import json
from cassiopeia import baseriotapi


class User:
    """Encapsulates the relevant information for a user."""
    def __init__(self, region, username, mastery):
        self.region = region
        self.username = username
        self.mastery = mastery


def _args_are_sane(arguments):
    """Ensures command line arguments are sane values."""
    supportedCommands = [ 'gen', 'add' ]
    supportedRegions = [
        'br', 'eune', 'euw', 'lan', 'las', 'na', 'oce', 'tr'
    ]
    champConfigFile = 'data/' + arguments[1] + '.ini'

    try:
        champConfig = open(champConfigFile)
    except FileNotFoundError:
        print(
            'Could not find an ini file for {0}'.format(arguments[1]),
            file=sys.stderr
        )
        return False
    champConfig.close()

    if arguments[2].lower() not in supportedCommands:
        print('Available commands are ', file=sys.stderr)
        return False

    if arguments[1] == 'add':
        if arguments[2].lower() not in supportedRegions:
            print(
                '{0} is not a supported region'.format(arguments[2]),
                file=sys.stderr
            )
            return False

    return True


def add_user(key, userData, region, newUsers):
    """Adds user data from the api to a dict."""
    region = region.lower()

    for username in newUsers:
        newUsers[newUsers.index(username)] = username.lower()

    # Set key
    baseriotapi.set_api_key(key)

    # Get user data
    baseriotapi.set_region(region)
    fetchedUserData = baseriotapi.get_summoners_by_name(newUsers)

    for username in newUsers:
        try:
            userData[region][fetchedUserData[username].name] = \
                str(fetchedUserData[username].id)
        except KeyError:
            print(
                'Unable to add data for {0}'.format(username),
                file=sys.stderr
            )

    return userData


def get_user_mastery_scores(key, userData, champId):
    """Takes a riot api key and a json of user information and
        returns a list<genchamplb.Users>.
    """
    users = []

    # Set key
    baseriotapi.set_api_key(key)

    # Iterate over regions in user data
    for region in userData:
        baseriotapi.set_region(region)

        # Iterate over user IDs in region data
        for username, userId in userData[region].items():
            try:
                mastery = baseriotapi.get_champion_mastery(
                        int(userId),
                        champId
                    ).championPoints
            except APIError:
                print(
                    'Unable to get user mastery for {0}'.format(username),
                    file=sys.stderr
                )
            users.append(User(region.upper(), username, mastery))

    # Sort users by mastery
    users = sorted(users, key=lambda user: user.mastery, reverse=True)

    return users


def format_as_json(users):
    """Takes a list<User> and returns a dict with the leaderboard index
    as the key.
    """
    leaderboard = dict()

    leaderboard['Time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

    for user in users:
        userIndex = str(users.index(user) + 1)
        leaderboard[userIndex] = dict()
        leaderboard[userIndex]["Name"] = user.username
        leaderboard[userIndex]["Mastery"] = user.mastery

    return leaderboard


def format_as_reddit_table(users):
    """Takes a list<User> and returns a nicely formatted reddit table."""
    leaderboard = '\\# | **Summoner Name** | **Server** | **Points**\n'
    leaderboard += '--:|--|--|--'
    index = 1

    for user in users:
        leaderboard += '\n{0} | {1} | {2} | {3}'.format(
            str(index),
            user.username,
            user.region,
            format(user.mastery, ',d')
        )
        index += 1

    return leaderboard


if __name__ == '__main__':
    if _args_are_sane(sys.argv):
        configFile = 'data/' + sys.argv[1] + '.ini'

        config = configparser.ConfigParser()
        config.read(configFile)

        key = config['Authentication']['RiotKey']

        champId = config['Leaderboard']['ChampionID']
        outStyle = config['Leaderboard']['Output']

        userDataFilePath = config['Files']['UserData']
        outputFilePath = config['Files']['OutputFile']

        with open(userDataFilePath) as userDataFile:
            userData = json.load(userDataFile)

        if sys.argv[2] == 'add':
            userData = add_user(key, userData, sys.argv[3], sys.argv[4:])

            with open(userDataFilePath, 'w') as userDataFile:
                json.dump(userData, userDataFile, sort_keys=True, indent=4)

        elif sys.argv[2] == 'gen':
            users = get_user_mastery_scores(key, userData, champId)

            if outStyle == 'console':
                print(format_as_reddit_table(users))

            elif outStyle == 'json':
                with open(outputFilePath, 'w') as outputFile:
                    json.dump(
                        format_as_json(users), outputFile, indent=4
                    )

            elif outStyle == 'reddit':
                with open(outputFilePath, 'w') as outputFile:
                    outputFile.write(format_as_reddit_table(users))
