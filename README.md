# E4GL BFACP to Cloudflare Zero Trust Syncer
[![Discord](https://img.shields.io/discord/388757799875903489.svg?colorB=7289DA&label=Discord&logo=Discord&logoColor=7289DA&style=flat-square)](https://discord.e4gl.com/)
[![Docker Pulls](https://img.shields.io/docker/pulls/hedius/bfacpcloudflaresync.svg?style=flat-square)](https://hub.docker.com/r/hedius/bfacpcloudflaresync/)

This project syncs users of your Battlefield Admin Control panel
to Cloudflare ZeroTrust access groups. Syncs are performed once
per minute to apply changes asap to the gateway.
An internal cache is used to hold the state at Cloudflare
in memory to reduce requests to Cloudflare.

It is possible to assign a BFACP role to several
Cloudflare access groups.
Furthermore, several roles can be assigned to an
access group.

Follow the setup to get this tool running.

# Setup
## docker (docker-compose)
 1. clone the repository
 2. adjust docker-compose.yml with your settings if needed
    - `vim docker-compose.yml`
 3. `cp config.ini.example config.ini` and adjust the config.
 3. sudo docker-compose up -d

## Configuration
```ini
[AdKatsDB]
host =
port = 3306
user =
pw =
db =

[Cloudflare]
# Cloudflare API token
# Needs edit permissions for : account - access: organisation, identity providers and groups
# + Include your ZeroTrust account
token =
# The ID of your ZeroTrust account.
# You can extract it from the URL:
# https://one.dash.cloudflare.com/{account_id}/home
account_id =

[GroupMapping]
# Mapping between access groups and BFACP groups
# Key = Access Group
# Value = BFACP roles/groups with access to this group
# Seperator between groups: ,
# Example:
Admin = First Tier Admin, Second Tier Admin
Management = Server Management
```

## Updating
1. sudo docker-compose down --rmi all
2. git pull
3. sudo docker-compose up -d

# License

This project is free software and licensed under the GPLv3.
