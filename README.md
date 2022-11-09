# Outline Manager
Simple Outline Manager Bot for Telegram

## Why?
Outline is a working vpn that you can use in IR, but it lacks of cross platform support for it's manager.
So I decided to write a telegram bot using it's api to be able to manage my clients from where I want.
This approach also has a bug that how can I share the key since everything is filtered for that you can 
see my other repo in future!

## Installation
Install docker (if you don't have)
```
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```
create a .env file in root directory with config below
```
TOKEN=xxx
api_url=xxx
certSha256=xxx
admins=["xxx", "xxx"]
```
then the final command
```
docker compose up -d
```
and you are ready to go!

## Bot Commands
Bot commands that are implemented 
```
get_server_info - Get server info as mentioned
get_keys - Get all available keys
create_key - [name] Create a new key specify the name afterwards
delete_key - [key_id] Delete the key
rename_key - [key_id, name] Edits access key name
get_transferred_data - Servers all data usage
```
