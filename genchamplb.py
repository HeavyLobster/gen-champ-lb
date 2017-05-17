#!/usr/bin/python
"""A CLI for libchampmastery"""

__version__ = '0.0a1'
__author__ = 'Heavy Lobster'

import sys
import time
import configparser
import json
import libchampmastery


def _args_are_sane(arguments):
    """Ensures command line arguments are sane values."""
    supportedCommands = [ 'gen', 'add', 'upd' ]
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
            user['name'],
            user['region'].upper(),
            format(user['mastery'], ',d')
        )
        index += 1

    return leaderboard


def main():
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

        libchampmastery.set_key(key)

        if sys.argv[2] == 'add':
            userData = libchampmastery.add_users(userData, sys.argv[3], sys.argv[4:])

            with open(userDataFilePath, 'w') as userDataFile:
                json.dump(userData, userDataFile, sort_keys=True, indent=4)

        elif sys.argv[2] == 'gen':
            users = libchampmastery.sort_users(userData)

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

        elif sys.argv[2] == 'upd':
            if len(sys.argv) == 3:
                userData = libchampmastery.update_all_users(userData, champId)

            elif len(sys.argv) > 3:
                userData = libchampmastery.update_region(userData, sys.argv[3], champId)

            elif len(sys.argv) > 4:
                userData = libchampmastery.update_single_user(userData, sys.argv[3], sys.argv[4], champId)

            with open(userDataFilePath, 'w') as userDataFile:
                json.dump(userData, userDataFile, sort_keys=True, indent=4)


if __name__ == '__main__':
    main()
