import requests


class CloudflareException(Exception):
    pass


class GroupNotFound(CloudflareException):
    pass


class Cloudflare:
    """
    Cloudflare connector
    """
    def __init__(self, token, account_id):
        """
        :param token: API token
        :param account_id: ZeroTrust account ID
        """
        self._token = token
        self.account_id = account_id

        self.root = 'https://api.cloudflare.com/client/v4/'

        self._header = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def get_group_by_name(self, name):
        """
        Pull a given access group by name
        :param name:
        :return: raw data
        :raise GroupNotFound: if the group does not exist
        :raise CloudflareException: if the return code != 200
        """
        r = requests.get(self.root + f'accounts/{self.account_id}/access/groups',
                         headers=self._header)
        if r.status_code != 200:
            raise CloudflareException(f'Failed to retrieve group: {r.text}')
        for group in r.json()['result']:
            if group['name'].lower() == name.lower():
                return group
        raise GroupNotFound(name)

    def update_group_members(self, uuid, name, members):
        """
        Update the members of the include rule for the given access group.
        :param uuid: UUID of the access group
        :param name: name of the access group
        :param members: List containing the members of the access group
        :raise CloudflareException: if the return code != 200
        """
        data = {
           'exclude': [],
           'include': [{'email': {'email': x}} for x in members],
           'name': name,
           'require': []
        }

        r = requests.put(self.root + f'accounts/{self.account_id}/access/groups/{uuid}',
                         json=data, headers=self._header)
        if r.status_code != 200:
            raise CloudflareException(f'Failed to update group: {r.text}')
