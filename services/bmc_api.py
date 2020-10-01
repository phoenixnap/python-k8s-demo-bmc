#!/usr/local/bin/python
"""Module providing calls available on BMC api."""
import json
from utils.bcolors import bcolors
from utils import files
from retrying import retry

environment = {'dev': {'url_path': 'https://api-dev.phoenixnap.com/bmc/v1beta/'},
               'prod': {'url_path': ' https://api.phoenixnap.com/bmc/v1beta/'}}


def get_servers(session, env='dev') -> str:
    """List all servers owned by account."""
    response = __get(session, environment[env]['url_path'] + 'servers')
    return __handle_response(response)


def get_server(session, server_id: str, env='dev') -> str:
    """Get server by ID."""
    response = __get(session, environment[env]['url_path'] + 'servers/{}'.format(server_id))
    return __handle_response(response)


def __handle_response(response):
    if response.status_code != 200:
        raise Exception(print_error(response))
    return response.json()


def __do_create_server(session, server, env):
    response = __post(session, (environment[env]['url_path'] + 'servers'), json.dumps(server))
    if response.status_code != 200:
        print(f"{bcolors.FAIL} Error creating server: {json.dumps(response.json())} {bcolors.ENDC}")
    else:
        files.save_server_provisioned(response.json())
        print(f"{bcolors.OKBLUE} {json.dumps(response.json(), indent=2)} {bcolors.ENDC}")
        return response.json()


def create_servers(futures, pool, session, servers: list, env="dev") -> list:
    """Create (request) new server for account."""
    for server in servers:
        futures.append(pool.submit(__do_create_server, session, server, env))


def delete_all_servers(session, env):
    """Delete all servers."""
    servers = files.load_servers_provisioned()

    for server in servers:
        response = __delete(session, environment[env]['url_path'] + 'servers/{}'.format(server['id']))
        if response.status_code != 200:
            # raise Exception(utils.print_error(response))
            print(f"{bcolors.FAIL} Error deleting server {bcolors.ENDC}")
        print(f"{bcolors.FAIL} {json.dumps(response.json())} {bcolors.ENDC}")


def retry_if_bad_request(response):
    print(f"Status code {response.status_code} on {response.request} to {response.url}. Retrying")
    return response.status_code == 502 or response.status_code == 409


@retry(retry_on_result=retry_if_bad_request, stop_max_attempt_number=5, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def __get(session, url: str):
    return session.get(url)


@retry(retry_on_result=retry_if_bad_request, stop_max_attempt_number=5, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def __post(session, url: str, payload):
    return session.post(url, data=payload)


@retry(retry_on_result=retry_if_bad_request, stop_max_attempt_number=5, wait_exponential_multiplier=1000, wait_exponential_max=10000)
def __delete(session, url: str):
    return session.delete(url)


def print_error(response) -> str:
    """Prints the error returned from an API call"""
    return 'Error: {}. \n {}'.format(response.status_code, response.json())
