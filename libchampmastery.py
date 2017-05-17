"""A library for looking up champion mastery data."""

__version__ = '0.0a1'
__author__ = 'Heavy Lobster'

import sys
from cassiopeia import baseriotapi
from cassiopeia.type.api import exception


def set_key(newKey):
    """Set the key to use for the Riot API."""
    set_key.key = newKey
    return


def add_users(userData, region, newUsers):
    """Add user data from the API to a dict.

    Args:
        userData (dict): The dictionary to work with.
        region (string): The region to work with.
        newUsers (list<string>): A list of up to 40 names to look up.

    Returns:
        dict: The original dict with additional users.
    """
    # Raise ValueError if there are more than 40 names to look up
    if len(newUsers) > 40:
        raise ValueError('More than 40 usernames passed to add_users()')

    # Pre-process arguments
    region = region.lower()

    for username in newUsers:
        newUsers[newUsers.index(username)] = username.lower()

    # Set up baseriotapi
    baseriotapi.set_api_key(set_key.key)
    baseriotapi.set_region(region)

    # Get user data
    fetchedUserData = baseriotapi.get_summoners_by_name(newUsers)

    # Initialize an empty dict for the region if one doesn't exist yet
    if region not in userData:
        userData[region] = dict()

    # Check for missing entries
    for username in newUsers:
        if username not in fetchedUserData:
            print(
                'Unable to fetch data for {0} {1}'.format(region, username),
                file=sys.stderr
            )

    # Make sure there's something in the dict
    if len(fetchedUserData) == 0:
        print('No data fetched, returning', file=sys.stderr)
        return userData

    # Iterate over fetched data, filling in information and defaults
    for userKey, userInfo in fetchedUserData.items():
        userData[region][userInfo.name.lower().replace(' ','')] = {
            'id': userInfo.id,
            'mastery': 0,
            'name': userInfo.name,
        }

    return userData


def rem_users(userData, region, rmUsers):
    """Remove user data by usernames."""
    region = region.lower()

    for username in rmUsers:
        rmUsers[rmUsers.index(username)] = username.lower().replace(' ','')

    for username in rmUsers:
        try:
            del userData[region][username]
        except KeyError:
            print(
                'Could not find {0} to be deleted'.format(username),
                file=sys.stderr
            )

    return userData


def update_single_user(userData, region, username, champId):
    """Update a single user's mastery score.

    Args:
        userData (dict): The user data to work with.
        region (string): The user's region.
        username (string): The username to look up.
        champId (ing): The champion for which to get mastery points.

    Returns:
        dict: The original dict with the updated mastery score."""
    username = username.lower().replace(' ','')

    # Set up baseriotapi
    baseriotapi.set_api_key(set_key.key)
    baseriotapi.set_region(region)

    try:
        mastery = baseriotapi.get_champion_mastery(
            int(userData[region][username]['id']),
            champId
        ).championPoints
        userData[region][username]['mastery'] = mastery
    except KeyError:
        print(
            'Could not find {0} to be updated'.format(username),
            file=sys.stderr
        )

    return userData


def update_region(userData, region, champId):
    """Update the mastery points of every user in one region.

    Args:
        userData (dict): The user data to work with.
        region (string): The region to update.
        champId (int): The champion for which to get mastery points.

    Returns:
        dict: The original dict with updated mastery scores.
    """
    # Set up baseriotapi
    baseriotapi.set_api_key(set_key.key)
    baseriotapi.set_region(region)

    # Iterate over users in a region
    for username, userInfo in userData[region].items():
        try:
            userInfo['mastery'] = baseriotapi.get_champion_mastery(
                int(userInfo['id']),
                champId
            ).championPoints
        except exception.APIError:
            print(
                'Unable to get user mastery for {0} {1}'.format(region, username),
                file=sys.stderr
            )

    return userData


def update_all_users(userData, champId):
    """Update the mastery points of every user in a dict.

    Args:
        userData (dict): The user data to iterate over.
        champId (int): The champion for which to get mastery points.

    Returns:
        dict: The original dict with updated mastery scores.
    """
    # Set key
    baseriotapi.set_api_key(set_key.key)

    # Iterate over regions in user data
    for region in userData:
        baseriotapi.set_region(region)

        # Iterate over user IDs in region data
        for username, userInfo in userData[region].items():
            try:
                userInfo['mastery'] = baseriotapi.get_champion_mastery(
                    int(userInfo['id']),
                    champId
                ).championPoints
            except exception.APIError:
                print(
                    'Unable to get user mastery for {0} {1}'.format(region, username),
                    file=sys.stderr
                )

    return userData


def sort_users(userData):
    """Sorts the users from a dict into an ordered list.

    Args:
        userData (dict): The user data to work with.

    Returns:
        list<dict>: The user data sorted into a list of dict objects.
    """
    users = []

    # Iterate over regions
    for region, regionUsers in userData.items():
        # Iterate over users in the region
        for username, userInfo in regionUsers.items():
            userDict = {
                'id': userInfo['id'],
                'region': region,
                'name': userInfo['name'],
                'mastery': userInfo['mastery'],
            }
            users.append(userDict)

    return sorted(users, key=lambda user: int(user['mastery']), reverse=True)
