import json
import os

FILE_NAME = "conf/servers_provisioned.json"


def delete_servers_provisioned_file():
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)


def save_server_provisioned(server):
    servers = load_servers_provisioned()
    servers.append(server)
    with open(FILE_NAME, 'w+') as fp:
        json.dump(servers, fp)


def load_servers_provisioned() -> list:
    __read_servers_provisioned_files()
    with open(FILE_NAME, 'r') as file:
        try:
            data = json.load(file)
        except:
            data = []
    return data


def __read_servers_provisioned_files():
    if not os.path.exists(FILE_NAME):
        print(f"created {FILE_NAME}")
        open(FILE_NAME, 'w')