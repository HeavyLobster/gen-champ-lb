#!/usr/bin/python
"""A CLI for libchampmastery."""

__version__ = "0.0a3"
__author__ = "Heavy Lobster"

import sys
import time
import configparser
import json

import libchampmastery


def _args_are_sane(arguments):
    """Ensures command line arguments are sane values."""
    commands = ("gen", "add", "upd", "del")
    champConfigFile = f"data/{arguments[1]}.ini"

    try:
        champConfig = open(champConfigFile)
    except FileNotFoundError:
        print(
            f"Could not find an ini file for {arguments[1]}",
            file=sys.stderr
        )
        return False
    champConfig.close()

    if arguments[2].lower() not in commands:
        print(
            "Available commands are {commands}",
             file=sys.stderr
        )
        return False

    if arguments[2] == "add":
        if arguments[3].lower() not in libchampmastery.regions:
            print(
                f"{arguments[3]} is not a supported region",
                file=sys.stderr
            )
            return False

    return True


def format_as_json(users):
    """Converts a sorted list of users into a dict.

    Args:
        users (list): A sorted list of users and associated data.

    Returns:
        dict: A dict with the users' position in the list as the key.
    """
    leaderboard = dict()

    leaderboard["time"] = str(int(time.time()))

    for user in users:
        userIndex = str(users.index(user) + 1)
        leaderboard[userIndex] = dict()
        leaderboard[userIndex]["region"] = user
        leaderboard[userIndex]["name"] = user.username
        leaderboard[userIndex]["mastery"] = user.mastery

    return leaderboard


def format_as_reddit_table(users):
    """Formats a list as a nicely formatted Reddit table.

    Args:
        users (list): A sorted list of users and associated data.

    Returns:
        string: A nicely formatted Reddit table.
    """
    leaderboard = "\\# | **Summoner Name** | **Server** | **Points**\n"
    leaderboard += "--:|--|--|--"
    index = 1

    for user in users:
        mastery = format(user["mastery"], ",d")
        leaderboard += (
            f"\n{str(index)} | {user['name']} | "
            f"{user['region'].upper()} | {mastery}"
        )
        index += 1

    return leaderboard


def main():
    if not _args_are_sane(sys.argv):
        return

    configFile = f"data/{sys.argv[1]}.ini"

    config = configparser.ConfigParser()
    config.read(configFile)

    key = config["Authentication"]["RiotKey"]

    champId = int(config["Leaderboard"]["ChampionID"])
    outStyle = config["Leaderboard"]["Output"]

    userDataFilePath = config["Files"]["UserData"]
    outputFilePath = config["Files"]["OutputFile"]

    with open(userDataFilePath) as userDataFile:
        userData = json.load(userDataFile)

    if sys.argv[2] == "add":
        api = libchampmastery.ApiInterface(key)
        for username in sys.argv[4:]:
            userInfo = api.user(sys.argv[3], username, champId)
            nameKey = userInfo["name"].lower().replace(" ", "")
            userData[nameKey] = userInfo
        with open(userDataFilePath, "w") as userDataFile:
            json.dump(userData, userDataFile, sort_keys=True, indent=4)

    elif sys.argv[2] == "gen":
        if len(sys.argv) == 3:
            users = libchampmastery.sort(userData)
        elif len(sys.argv) == 4:
            for user, userInfo in userData.items():
                if userInfo["region"] != sys.argv[3].lower():
                    del userData[user]
            users = libchampmastery.sort(userData, sys.argv[3])

        if outStyle == "console":
            print(format_as_reddit_table(users))
        elif outStyle == "json":
            with open(outputFilePath, "w") as outputFile:
                json.dump(
                    format_as_json(users), outputFile, indent=4
                )
        elif outStyle == "reddit":
            with open(outputFilePath, "w") as outputFile:
                outputFile.write(format_as_reddit_table(users))

    elif sys.argv[2] == "upd":
        api = libchampmastery.ApiInterface(key)
        if len(sys.argv) == 3:
            for username, userInfo in userData.items():
                mastery = api.mastery(
                    userInfo["region"], champId, userInfo["id"]
                )
                userInfo["mastery"] = mastery
        elif len(sys.argv) == 4:
            for username, userInfo in userData.items():
                if userInfo["region"] == sys.argv[3].lower():
                    mastery = api.mastery(
                        userInfo["region"], champId, userInfo["id"]
                    )
                    userInfo["mastery"] = mastery
        else:
            for username in sys.argv[4:]:
                userId = userData[username]["id"]
                mastery = api.mastery(sys.argv[3], champId, userId)
                userData[username]["mastery"] = mastery

        with open(userDataFilePath, "w") as userDataFile:
            json.dump(userData, userDataFile, sort_keys=True, indent=4)

    elif sys.argv[2] == "del":
        for username in sys.argv[4:]:
            if userData[username]["region"] == sys.argv[3].lower():
                print(
                    f"Removing data for {userData[username]['name']}"
                )
                del userData[username]
            else:
                print(
                    f'Could not find "{username}" '
                    f'in {sys.argv[3].lower()}'
                )

        with open(userDataFilePath, "w") as userDataFile:
            json.dump(userData, userDataFile, sort_keys=True, indent=4)


if __name__ == "__main__":
    main()
