"""A library for looking up champion mastery data."""

__version__ = '0.0a3'
__author__ = 'Heavy Lobster'

import sys

import apiinterface


def set_key(newKey):
    """Set the key to use for the Riot API."""
    apiinterface.key = newKey


def _check_key_exists():
    """Make sure a key has been set."""
    try:
        if apiinterface.key:
            return None
    except AttributeError:
        raise AttributeError('No key set, use libchampmastery.set_key(key)')


def add_user(userData, region, newUser):
    """Fetch data for a user by username.

    Args:
        userData (dict): The user data to work with.
        region (string): The region to work with.
        newUser (string): The username to look up.

    Returns:
        dict: The new users in a properly formatted dict.
    """
    _check_key_exists()

    # Pre-process arguments
    region = region.lower()
    newUser = newUser.lower().replace(' ', '')

    # Get user data
    fetchedUserData = apiinterface.get_user(region, newUser)

    # Initialize an empty dict for the region if one doesn't exist yet
    if region not in userData:
        userData[region] = dict()

    # Fill in information and defaults
    userData[region][fetchedUserData["name"].lower().replace(' ','')] = {
        'id': fetchedUserData["id"],
        'mastery': 0,
        'name': fetchedUserData["name"],
    }

    return userData


def del_users(userData, region, rmUsers):
    """Remove user data by usernames."""
    region = region.lower()

    # Pre-process names
    for username in rmUsers:
        rmUsers[rmUsers.index(username)] = username.lower().replace(' ','')

    # Iterate over usernames
    for username in rmUsers:
        try:
            del userData[region][username]
        except KeyError:
            print(
                'Could not find {0} to be deleted'.format(username),
                file=sys.stderr
            )

    return userData


def _fetch_mastery(champId, region, userId):
    """Fetch a user's mastery score, retrying if it fails."""
    _check_key_exists()

    mastery = -1

    failedAttempts = 0
    while mastery == -1:
        try:
            mastery = apiinterface.get_mastery(
                region,
                champId,
                userId
            )['championPoints']
        except Exception:
            if failedAttempts < 3:
                print(
                    (f'Unable to get data for {userInfo["name"]}, '
                      'trying {3 - failedAttempts} more times...'),
                    file=sys.stderr
                )
                failedAttempts += 1
            else:
                raise LookupError(f'Unable to get data for '
                                   '{userInfo["name"]} in '
                                   '{region.upper()}')

    return mastery


def update_mastery(userData, champId, region=None, username=None):
    """Update mastery scores.

    Args:
        userData (dict): The user data to work with.
        champId (int): ID for the champion to get scores for.
        region (string, optional): The region to limit updates to.
            Required if username is supplied.
        username (string, optional): The specific user to update.

    Returns:
        dict: The original dict with updated mastery scores.
    """
    # Pre-process parameters
    if username != None:
        username = username.lower().replace(' ', '')
        # Make sure region is set
        if region == None:
            raise TypeError('update_mastery(): username set without region')
    if region != None:
        region = region.lower()

    # Case switcher for different parameters
    if username != None:
        userData[region][username]['mastery'] = _fetch_mastery(
            champId, region, userData[region][username]['id']
        )

    elif region != None:
        for username, userInfo in userData[region].items():
            userInfo['mastery'] = _fetch_mastery(champId , region, userInfo['id'])

    else:
        for region in userData:
            for username, userInfo in userData[region].items():
                userInfo['mastery'] = _fetch_mastery(champId , region, userInfo['id'])

    return userData


def sort_users(userData, region=None):
    """Sorts the users from a dict into an ordered list.

    Args:
        userData (dict): The user data to work with.
        region (string): The region for which to return users.

    Returns:
        list<dict>: The user data sorted into a list of dict objects.
    """
    users = []

    # Populate list of users
    # If no region is specified, return users from all regions
    if region == None:
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

    # Else, return the users from just the specified region
    else:
        for username, userInfo in userData[region.lower()].items():
            userDict = {
                'id': userInfo['id'],
                'region': region,
                'name': userInfo['name'],
                'mastery': userInfo['mastery'],
            }
            users.append(userDict)

    # Sort list
    users = sorted(
        users,
        key=lambda user: int(user['mastery']),
        reverse=True
    )

    return users
