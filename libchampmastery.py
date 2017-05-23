"""A library for looking up champion mastery data."""

__version__ = '0.0a2'
__author__ = 'Heavy Lobster'

import sys
from cassiopeia import baseriotapi
from cassiopeia.type.api import exception


def set_key(newKey):
    """Set the key to use for the Riot API."""
    set_key.key = newKey


def _check_key_exists():
    """Make sure a key has been set."""
    try:
        if set_key.key:
            return None
    except AttributeError:
        raise AttributeError('No key set, use libchampmastery.set_key(key)')


def add_users(userData, region, newUsers):
    """Fetch data for users by username.

    Args:
        userData (dict): The user data to work with.
        region (string): The region to work with.
        newUsers: A string containing a username or a list<string> of several
            usernames to look up.

    Returns:
        dict: The new users in a properly formatted dict.
    """
    _check_key_exists()

    # Pre-process arguments
    region = region.lower()
    if type(newUsers).__name__ == 'str':
        newUsers = [newUsers.lower().replace(' ', '')]
    else:
        for username in newUsers:
            newUsers[newUsers.index(username)] = username.lower()

    # Set up baseriotapi
    baseriotapi.set_api_key(set_key.key)
    baseriotapi.set_region(region)

    # Get user data 40 users at a time
    fetchedUserData = dict()
    for pos in range(0, len(newUsers), 40):
        fetchedUserData.update(
            baseriotapi.get_summoners_by_name(newUsers[pos:pos + 40])
        )

    # Make sure there's something in the dict
    if len(fetchedUserData) == 0:
        raise LookupError('Unable to fetch any users')

    # Check for missing entries
    for username in newUsers:
        if username not in fetchedUserData:
            print(
                'Unable to fetch data for {0} {1}'.format(region, username),
                file=sys.stderr
            )

    # Initialize an empty dict for the region if one doesn't exist yet
    if region not in userData:
        userData[region] = dict()

    # Iterate over fetched data, filling in information and defaults
    for userKey, userInfo in fetchedUserData.items():
        userData[region][userInfo.name.lower().replace(' ','')] = {
            'id': userInfo.id,
            'mastery': 0,
            'name': userInfo.name,
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

    # Set up baseriotapi
    baseriotapi.set_api_key(set_key.key)
    baseriotapi.set_region(region)

    while mastery == -1:
        try:
            mastery = baseriotapi.get_champion_mastery(
                userId,
                champId
            ).championPoints
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


def update_single_user(userData, region, username, champId):
    """Update a single user's mastery score.

    Args:
        userData (dict): The user data to work with.
        region (string): The user's region.
        username (string): The username to look up.
        champId (int): The champion for which to get mastery points.

    Returns:
        dict: The original dict with the updated mastery score.
    """
    _check_key_exists()

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
    _check_key_exists()

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
    _check_key_exists()

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
