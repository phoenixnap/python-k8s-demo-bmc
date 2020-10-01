# Bare Metal Cloud Demo Scripts

The purpose of this repo is show a demo of provisioning servers through BMC API.

This script provide a kubernetes cluster of 3 Ubuntu servers (1 master node and 2 workers nodes) with a Wordpress application running.

To run the script you need a valid API credentials for https://api.phoenixnap.com/bmc/v0/

### Requirements

- Python 3 (https://www.python.org/downloads/)

- Valid API credentials

### Setup

1. Download the repo ```git clone git@gitlab.com:phoenixnap/bare-metal-cloud/devops-days-scritps.git```

2. Execute the command ```pip install -r requirements.txt```

3. Set your credentials in credentials.conf

4. Set default public key in server-settings.conf, you can get it with ```cat ~/.ssh/id_rsa.pub```

5. Execute the command ```python3 k8s-demo.py```

### Script details

##### K8S setup progress 
When the script will be ready the master node and has configured the local ```kubectl```, the script will be open a new terminal window with the K8S setup progress (be patient to see all components, the script is working on it). You can close this new terminal whenever you want without affect to the script execution. 

##### URLs
After prepare the infrastructure, software and check that the cluster is correctly setup, the script will be provide two URLs and a token to access to the kubernetes admin dashboard and the Wordpress site

- **Kubernetes admin dashboard URL**: 
    1. Copy and paste the URL (including the port) provided after ```KUBERNETES DASHBOARD INFO``` message in Firefox browser
    2. You will see a certificate warning, click in ```Advance...``` and ```Accept the risk and continue``` buttons
    3. Select the token option and paste the token provided by the script.

- **Wordpress URL**: 
    1. Copy and paste the URL provided after ```WORDPRESS DASHBOARD INFO``` message in Firefox browser


### After the demo

Please release the servers with the command ```python3 k8s-demo.py -d0```
