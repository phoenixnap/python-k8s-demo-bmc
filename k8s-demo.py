#!/usr/local/bin/python
"""Script to generate X servers, configure them in a kubernetes cluster and deploy a wordpress."""

"""You have to install parallel-ssh"""
import argparse
import sched
import time
import requests
import ast
import subprocess
from datetime import datetime
from time import sleep
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from services import bmc_api_auth, bmc_api
from utils.bcolors import bcolors
from utils import files

scheduler = sched.scheduler(time.time, time.sleep)

REQUEST = requests.Session()
ENVIRONMENT = "prod"
VERBOSE_MODE = False
MAX_RETRIES = 1
NOW = datetime.now()


def parse_args():
    """Defines which arguments are needed for the script to run."""
    parser = argparse.ArgumentParser(
        description='BMC-API Demo')
    req_grp = parser.add_argument_group(title='optional arguments')
    req_grp.add_argument(
        '-d',
        '--delete_all',
        help='Delete all servers')
    parsed = parser.parse_args()

    return parsed


def main():
    """Method called from the main entry point of the script to do the required logic."""
    args = parse_args()
    delete_all = args.delete_all
    get_access_token(credentials["client_id"], credentials["client_secret"])
    if delete_all is not None:
        bmc_api.delete_all_servers(REQUEST, ENVIRONMENT)
        files.delete_servers_provisioned_file()
        return
    files.delete_servers_provisioned_file()
    check_kubectl_local()
    servers = list()
    pool = ThreadPoolExecutor()
    futures_requests = []
    print(bcolors.WARNING + "Creating servers..." + bcolors.ENDC)
    bmc_api.create_servers(futures_requests, pool, REQUEST, data["servers"], ENVIRONMENT)
    futures_setups = []
    requests_counter = 0
    for request in as_completed(futures_requests):
        if request.result() is not None:
            requests_counter += 1
            json_server = request.result()
            print(bcolors.WARNING + "Server created, provisioning {}...".format(json_server['hostname']) + bcolors.ENDC)
            if requests_counter == server_settings['servers_quantity']:
                print(bcolors.WARNING + "Waiting for servers to be provisioned..." + bcolors.ENDC)
            futures_setups.append(pool.submit(__do_setup_host, servers, request.result()))
    wait(futures_setups)
    for server in servers:
        print(bcolors.OKBLUE + bcolors.BOLD + "Setup servers done" + bcolors.ENDC)
        if not server['joined']:
            print(bcolors.WARNING + "Adding node" + bcolors.ENDC)
            join_nodes(data['master_ip'], server)
        elif server['master']:
            install_wordpress()
            print(bcolors.OKBLUE + bcolors.BOLD + "Wordpress installed" + bcolors.ENDC)
    if len(servers) > 0:
        setup_master_dashboard(data['master_ip'])
        print(bcolors.OKBLUE + bcolors.BOLD + "Kubernetes dashboard installed" + bcolors.ENDC)
        #Fix to ensure coredns and wordpress works correctly
        run_shell_command(['kubectl scale deployment.apps/coredns -n kube-system --replicas=0'])
        run_shell_command(['kubectl scale deployment.apps/coredns -n kube-system --replicas=1'])
        run_shell_command(['kubectl scale deployment.apps/wordpress -n wordpress --replicas=0'])
        run_shell_command(['kubectl scale deployment.apps/wordpress -n wordpress --replicas=1'])
        check_system(servers)
        show_k8s_dashboard_info()
        show_wordpress_info()


def __do_setup_host(servers, json_server):
    if json_server is not None:
        json_server['master'] = False
        json_server['joined'] = False
        servers.append(json_server)
        setup_host(json_server)
    return json_server


def setup_hosts(servers):
    pool = ThreadPoolExecutor()
    futures = []
    for json_server in servers:
        futures.append(pool.submit(setup_host, json_server))
    wait(futures)
    return futures, pool


def join_nodes(master_host, json_server):
    if not json_server['master']:
        token = get_tokens(master_host)
        print(bcolors.WARNING + "Joining node {} to master node".format(json_server['hostname']) + bcolors.ENDC)
        join_to_cluster(json_server['publicIpAddresses'][0], master_host, token)


def get_master_host(servers):
    for json_server in servers:
        if json_server['master']:
            return json_server['publicIpAddresses'][0]


def get_access_token(client, password):
    print(bcolors.WARNING + "Retrieving token" + bcolors.ENDC)
    # Retrieve an access token using the client Id and client secret provided.
    access_token = bmc_api_auth.get_access_token(client, password, ENVIRONMENT)
    # Add Auth Header by default to all requests.
    REQUEST.headers.update({'Authorization': 'Bearer {}'.format(access_token)})
    REQUEST.headers.update({'Content-Type': 'application/json'})


def setup_host(json_server):
    scheduler.enter(0, 1, wait_server_ready, (scheduler, json_server))
    scheduler.run()
    print(bcolors.OKBLUE + bcolors.BOLD + "Server provisioned {}".format(json_server['hostname']) + bcolors.ENDC)
    print(bcolors.WARNING + "Installing kubernetes in {}".format(json_server['hostname']) + bcolors.ENDC)
    install_basic_script(json_server['publicIpAddresses'][0])
    print(bcolors.OKBLUE + bcolors.BOLD + "Kubernetes installed {}".format(json_server['hostname']) + bcolors.ENDC)
    if json_server['master']:
        print(bcolors.WARNING + "Configure local kubernetes cli for connect to master" + bcolors.ENDC)
        setup_localhost(data['master_ip'])
        print(bcolors.OKBLUE + bcolors.BOLD + "Local kubernetes cli configured to connect to master" + bcolors.ENDC)
        setup_k8s_addons(data['master_ip'])
        print(bcolors.OKBLUE + bcolors.BOLD + "Add-ons installed, the master node is ready to use" + bcolors.ENDC)
    return json_server


def wait_server_ready(sched, server_data):
    json_server = bmc_api.get_server(REQUEST, server_data['id'], ENVIRONMENT)
    if json_server['status'] == "creating":
        scheduler.enter(2, 1, wait_server_ready, (sched, server_data,))
    elif json_server['status'] == "powered-on" and not data['has_a_master_server']:
        server_data['status'] = json_server['status']
        server_data['master'] = True
        server_data['joined'] = True
        data['has_a_master_server'] = True
        data['master_ip'] = json_server['publicIpAddresses'][0]
        data['master_hostname'] = json_server['hostname']
        print(
            bcolors.OKBLUE + bcolors.BOLD + "ASSIGNED MASTER SERVER: {}".format(data['master_hostname']) + bcolors.ENDC)
    else:
        server_data['status'] = json_server['status']


def setup_localhost(master_ip: str):
    run_shell_command(
        [ssh + 'ubuntu@{} \'sudo microk8s.kubectl config view --raw\' > ~/.kube/config'.format(master_ip)])
    run_shell_command(['sed -i \'s/127.0.0.1/{}/g\' ~/.kube/config'.format(master_ip)])
    run_shell_command(['gnome-terminal -e \'sh -c \"watch -n1 kubectl get all --all-namespaces -o wide; exec bash\"\''])


def check_system(servers: list):
    print("Checking k8s add-ons installation")
    if not is_k8s_addons_ready():
        print(bcolors.FAIL + "Error in kubernetes add-ons installation" + bcolors.ENDC)
        setup_k8s_addons(data['master_ip'])
    print("Checking wordpress installation")
    if not is_wordpress_ready():
        print(bcolors.FAIL + "Error in wordpress installation" + bcolors.ENDC)
        install_wordpress()
    print("Checking k8s dashboard installation")
    if not is_k8s_dashboard_ready():
        print(bcolors.FAIL + "Error in k8s dashboard installation" + bcolors.ENDC)
        setup_master_dashboard(data['master_ip'])
    print("Checking nodes connection")
    for server in servers:
        if not server['master'] and not is_node_ready(server['publicIpAddresses']):
            print(
                bcolors.FAIL + "Error in node {} communication installation".format(server['hostname']) + bcolors.ENDC)
            setup_host(server)
            join_nodes(data['master_ip'], server)


def is_k8s_addons_ready() -> bool:
    checks_list = list()
    checks_list.append('kubectl get services -l k8s-app=kube-dns -nkube-system | grep -i kube-dns')
    checks_list.append('kubectl get deployments -nkube-system | grep -i coredns')
    checks_list.append('kubectl get pods -nkube-system | grep -i coredns')
    checks_list.append('kubectl get pods -ningress | grep -i ingress')
    return checker_list(checks_list)


def is_k8s_dashboard_ready() -> bool:
    checks_list = list()
    checks_list.append('kubectl get services -nkube-system | grep -i kubernetes-dashboard')
    checks_list.append('kubectl get deployments -nkube-system | grep -i kubernetes-dashboard')
    checks_list.append('kubectl get pods -nkube-system | grep -i kubernetes-dashboard')
    return checker_list(checks_list)


def is_wordpress_ready() -> bool:
    checks_list = list()
    checks_list.append('kubectl get namespaces -nwordpress | grep -i wordpress')
    checks_list.append('kubectl get services -nwordpress | grep -i wordpress')
    checks_list.append('kubectl get deployments -nwordpress | grep -i wordpress')
    checks_list.append('kubectl get pods -nwordpress | grep -i wordpress')
    checks_list.append('kubectl get ingress -nwordpress | grep -i wordpress')
    checks_list.append('kubectl get services -nwordpress | grep -i mysql')
    checks_list.append('kubectl get deployments -nwordpress | grep -i mysql')
    checks_list.append('kubectl get pods -nwordpress | grep -i mysql')
    checks_list.append('kubectl get pv -nwordpress | grep -i mysql')
    checks_list.append('kubectl get pvc -nwordpress | grep -i mysql')
    return checker_list(checks_list)


def is_node_ready(worker_ips) -> bool:
    nodes = run_shell_command(['kubectl get nodes'], print_log=True)
    for worker_ip in worker_ips:
        if worker_ip in nodes:
            return True
    return False


def checker_list(check_list):
    for check in check_list:
        output = run_shell_command([check], print_log=True)
        if output == "":
            return False
    return True


def install_wordpress():
    print(bcolors.WARNING + "Installing wordpress" + bcolors.ENDC)
    run_shell_command(['kubectl create namespace wordpress'], print_log=True)
    run_shell_command(['kubectl apply -f ./wordpress.yaml -nwordpress'], print_log=True)


def install_basic_script(host_ip: str):
    run_shell_command([ssh + 'ubuntu@{} \'bash -s\' < ./scripts/basic.sh'.format(host_ip)], print_log=True)


def setup_k8s_addons(master_ip: str):
    print(
        bcolors.WARNING + "Installing k8s add-ons in master server: {}".format(data['master_hostname']) + bcolors.ENDC)
    run_shell_command([ssh + 'ubuntu@{} \'sudo microk8s.enable dns ingress\''.format(master_ip)],
                      print_log=True)


def setup_master_dashboard(master_ip: str):
    print(bcolors.WARNING + "Installing kubernetes dashboard" + bcolors.ENDC)
    run_shell_command([ssh + 'ubuntu@{} \'bash -s\' < ./scripts/master-dashboard.sh {}'.format(master_ip, master_ip)],
                      print_log=True)


def get_tokens(master_ip: str) -> str:
    run_shell_command([ssh + 'ubuntu@{} sudo microk8s.add-node'.format(master_ip)], print_log=True)
    return run_shell_command(
        [ssh + 'ubuntu@{} sudo cat /var/snap/microk8s/current/credentials/cluster-tokens.txt'.format(master_ip)],
        print_log=True)


def join_to_cluster(worker_ip: str, master_ip: str, token: str) -> str:
    return run_shell_command([ssh + 'ubuntu@{} sudo microk8s.join {}:25000/{}'.format(worker_ip, master_ip, token)],
                             print_log=True)


def read_dict_file(filename: str) -> dict:
    with open(filename, 'r') as f:
        s = f.read()
        return ast.literal_eval(s)


def check_kubectl_local():
    if run_shell_command(["command -v kubectl"]) == "":
        txt = input("Install kubectl in your computer? (y/n) ")
        if txt == "y":
            print(bcolors.WARNING + "Installing kubectl in local machine" + bcolors.ENDC)
            run_shell_command(['chmod +x ./scripts/kubectl-local.sh'])
            run_shell_command(['./scripts/kubectl-local.sh'])
            print(bcolors.OKBLUE + "Installed kubectl" + bcolors.ENDC)


def show_k8s_dashboard_info():
    print(bcolors.OKBLUE + bcolors.BOLD + "==== KUBERNETES DASHBOARD INFO ====" + bcolors.ENDC)
    token = run_shell_command(["kubectl -n kube-system get secret | grep default-token | cut -d \" \" -f1"])
    token = run_shell_command(["kubectl -n kube-system describe secret {}".format(token)])
    port = run_shell_command(
        ["kubectl -n kube-system describe service kubernetes-dashboard | grep NodePort | grep -Eo \'[0-9]{1,6}\'"])
    print("Dashboard URL: https://{}:{}".format(data["master_ip"], port))
    print("Token: {}".format(token))


def show_wordpress_info():
    print(bcolors.OKBLUE + bcolors.BOLD + "==== WORDPRESS DASHBOARD INFO ====" + bcolors.ENDC)
    print("URL: https://{}".format(data["master_ip"]))


def run_shell_command(commands: list, print_log: bool = VERBOSE_MODE, retries: int = 0) -> str:
    proc = subprocess.Popen(commands, stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    result = out.decode('UTF-8')
    if err:
        print(bcolors.FAIL + "Error executing: {}".format(*commands) + bcolors.ENDC)
        print(bcolors.FAIL + "{}".format(err.decode('UTF-8')) + bcolors.ENDC)
        if retries < MAX_RETRIES:
            print(bcolors.HEADER + "Retrying ({}/{})".format(retries, MAX_RETRIES) + bcolors.ENDC)
            sleep(0.2)
            retries = retries + 1
            return run_shell_command(commands, print_log, retries)
    if print_log:
        if result != "":
            print(bcolors.HEADER + "{}".format(result) + bcolors.ENDC)
        else:
            print(bcolors.HEADER + "Finished: {}".format(*commands) + bcolors.ENDC)
    return result


if __name__ == '__main__':
    server_settings = read_dict_file("server-settings.conf")
    credentials = read_dict_file("credentials.conf")
    servers_data = []
    for server in range(server_settings['servers_quantity']):
        server_data = {"hostname": "{}-{}".format(server_settings['hostname'], server+1),
                       "description": "{}".format(server_settings['description'], server+1),
                       "public": True,
                       "location": "PHX",
                       "os": "ubuntu/bionic",
                       "type": server_settings['server_type'],
                       "sshKeys": [server_settings['ssh-key']]}
        servers_data.append(server_data)
    data = {"has_a_master_server": False, "servers": servers_data, "master_ip": "", "master_hostname": ""}
    time = {"now": NOW}
    config = {}
    ssh = "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR "
    main()
