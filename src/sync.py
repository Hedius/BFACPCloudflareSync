import time
from argparse import ArgumentParser
from configparser import ConfigParser
from datetime import timedelta, datetime
from pathlib import Path
from typing import Tuple, List, Dict

from deepdiff.diff import DeepDiff
from loguru import logger

from src.Cloudflare import Cloudflare
from src.AdKatsDB import AdKatsDB


class CloudflareSync:
    """
    Sync BFACP users to Cloudflare ZeroTrust
    """
    def __init__(self, adk: AdKatsDB, api: Cloudflare, check_interval=60):
        """
        Init CloudflareSync
        :param adk: AdKatsDB connector
        :param api: Cloudflare connector
        :param check_interval: repeat check every x seconds
        """
        self.adk = adk
        self.api = api
        self.check_interval = check_interval

        # Cache for holding current state at CF - reduce requests
        # Apply changes faster
        self._cf_cache = {}

    def check(self, groups: Dict[str, List[str]]):
        """
        Sync users from the DB to Cloudflare every x seconds.
        :param groups: group setting. See readme.
        :return:
        """
        logger.info('Starting monitoring.')
        while True:
            for group, roles in groups.items():
                # Authorized users for this group
                authorized = self.adk.get_admin_emails(roles)

                # Refresh from api if needed
                if (group not in self._cf_cache
                        or (datetime.now() - self._cf_cache[group]['timestamp']) <= timedelta(minutes=30)):
                    api_data = self.api.get_group_by_name(group)
                    api_emails = [x['email']['email'] for x in api_data['include']]
                    self._cf_cache[group] = {
                        'id': api_data['id'],
                        'name': api_data['name'],
                        'timestamp': datetime.now(),
                        'include': api_emails
                    }
                api_data = self._cf_cache[group]
                diff = DeepDiff(api_data['include'], authorized)
                if len(diff) == 0:
                    continue

                logger.info(f'CORRECTING DIFF! {group}: ADD: {diff.get("iterable_item_added")}, '
                            f'RM: {diff.get("iterable_item_removed")}')
                logger.info(f'BFACP: {", ".join(authorized)}')
                logger.info(f'CF: {", ".join(api_data["include"])}')

                self.api.update_group_members(api_data['id'], api_data['name'], authorized)
                self._cf_cache.pop(group)
            time.sleep(self.check_interval)


def read_config(file_path: Path) -> Tuple[AdKatsDB, Cloudflare, Dict[str, List[str]]]:
    """
    Read the config
    :param file_path:
    :return: adk, cf, groups
    """
    parser = ConfigParser()
    parser.read(file_path)

    section = parser['AdKatsDB']
    adk = AdKatsDB(
        host=section['host'],
        port=int(section['port']),
        user=section['user'],
        pw=section['pw'],
        db=section['db'],
    )

    section = parser['Cloudflare']
    api = Cloudflare(
        token=section['token'],
        account_id=section['account_id']
    )

    groups = {}
    section = parser['GroupMapping']
    for key in section.keys():
        groups[key] = list(map(str.strip, section[key].split(',')))
    return adk, api, groups


def main():
    parser = ArgumentParser(description='E4GL Cloudflare Access Group Sync')
    parser.add_argument(
        '-c', '--config',
        help='Path to config file',
        required=True,
        dest='config'
    )
    args = parser.parse_args()

    adk, api, groups = read_config(args.config)
    syncer = CloudflareSync(adk, api)
    syncer.check(groups)


if __name__ == '__main__':
    main()
