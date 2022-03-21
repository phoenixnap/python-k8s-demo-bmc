<h1 align="center">
  <br>
  <a href="https://phoenixnap.com/bare-metal-cloud"><img src="https://user-images.githubusercontent.com/78744488/109779287-16da8600-7c06-11eb-81a1-97bf44983d33.png" alt="phoenixnap Bare Metal Cloud" width="300"></a>
  <br>
  Kubernetes on Bare Metal Cloud Demo Script
  <br>
</h1>

<p align="center">
Demo script for provisioning Bare Metal Cloud servers via API. This script creates a Kubernetes cluster consisting of 3 Ubuntu servers (1 master node and 2 workers nodes) with a WordPress installation.
</p>

<p align="center">
  <a href="https://phoenixnap.com/bare-metal-cloud">Bare Metal Cloud</a> •
  <a href="https://developers.phoenixnap.com/apis">API</a> •
  <a href="https://developers.phoenixnap.com/">Developers Portal</a> •
  <a href="http://phoenixnap.com/kb">Knowledge Base</a> •
  <a href="https://developers.phoenixnap.com/support">Support</a>
</p>

## Requirements

- [Bare Metal Cloud](https://bmc.phoenixnap.com) account
- [Python 3](https://www.python.org/downloads/)

## Creating a Bare Metal Cloud account

1. Go to the [Bare Metal Cloud signup page](https://support.phoenixnap.com/wap-jpost3/bmcSignup).
2. Follow the prompts to set up your account.
3. Use your credentials to [log in to Bare Metal Cloud portal](https://bmc.phoenixnap.com).

:arrow_forward: **Video tutorial:** [How to Create a Bare Metal Cloud Account](https://www.youtube.com/watch?v=RLRQOisEB-k)
<br>

:arrow_forward: **Video tutorial:** [Introduction to Bare Metal Cloud](https://www.youtube.com/watch?v=8TLsqgLDMN4)

## API Credentials

You need valid Bare Metal Cloud API credentials to use this script. Follow these steps to obtain your API credentials:

1. [Log in to the Bare Metal Cloud portal](https://bmc.phoenixnap.com).
2. On the left side menu, click on API Credentials.
3. Click the Create Credentials button.
4. Fill in the Name and Description fields, select the permissions scope and click Create.
5. In the table, click on Actions and select View Credentials from the dropdown to view the Client ID and Client Secret.

**Bare Metal Cloud Quick Start Guide**: [https://developers.phoenixnap.com/quick-start](https://developers.phoenixnap.com/quick-start)

## Setup

1. Execute the command: ```pip install -r requirements.txt```

2. Set your credentials in ```credentials.conf```.

3. Set a public key in ```server-settings.conf```, you can see your default public key with this command: ```cat ~/.ssh/id_rsa.pub```.

4. To execute the script, run this command: ```python3 k8s-demo.py```

## Script details

##### K8S setup progress 
Once the script is ready and the master node has configured the local ```kubectl```, the script will open a new terminal window which will display the K8S setup progress (be patient to see all components). The script execution will not tbe affected if you close th terminal window.

##### URLs
The script will check if the cluster is set up properly. You will get a URL to access the master node via web UI and a token to access to the Kubernetes admin dashboard, as well as the Wordpress installation.

- **Kubernetes admin dashboard URL**: 
    1. Copy the URL from the ```KUBERNETES DASHBOARD INFO``` and paste it into your browser.
    2. You will get a certificate warning since you don't have an SSL certificate. You can ignore the warning and click on ```Advance...``` and then ```Accept the risk and continue```.
    3. Select the token option and paste the token provided by the script.

- **Wordpress URL**: 
    1. Copy the URL from the ```WORDPRESS DASHBOARD INFO``` and paste it into your browser to access WordPress.

## Release

To release the servers, use the command: ```python3 k8s-demo.py -d0```.

## Bare Metal Cloud community

Become part of the Bare Metal Cloud community to get updates on new features, help us improve the platform, and engage with developers and other users.

- Follow [@phoenixNAP on Twitter](https://twitter.com/phoenixnap)
- Join the [official Slack channel](https://phoenixnap.slack.com)
- Sign up for our [Developers Monthly newsletter](https://phoenixnap.com/developers-monthly-newsletter)

### Resources

- [Product page](https://phoenixnap.com/bare-metal-cloud)
- [Instance pricing](https://phoenixnap.com/bare-metal-cloud/instances)
- [YouTube tutorials](https://www.youtube.com/watch?v=8TLsqgLDMN4&list=PLWcrQnFWd54WwkHM0oPpR1BrAhxlsy1Rc&ab_channel=PhoenixNAPGlobalITServices)
- [Developers Portal](https://developers.phoenixnap.com)
- [Knowledge Base](https://phoenixnap.com/kb)
- [Blog](https:/phoenixnap.com/blog)

### Documentation

- [API documentation](https://developers.phoenixnap.com/apis)

### Contact phoenixNAP

Get in touch with us if you have questions or need help with Bare Metal Cloud.

<p align="left">
  <a href="https://twitter.com/phoenixNAP">Twitter</a> •
  <a href="https://www.facebook.com/phoenixnap">Facebook</a> •
  <a href="https://www.linkedin.com/company/phoenix-nap">LinkedIn</a> •
  <a href="https://www.instagram.com/phoenixnap">Instagram</a> •
  <a href="https://www.youtube.com/user/PhoenixNAPdatacenter">YouTube</a> •
  <a href="https://developers.phoenixnap.com/support">Email</a> 
</p>

<p align="center">
  <br>
  <a href="https://phoenixnap.com/bare-metal-cloud"><img src="https://user-images.githubusercontent.com/81640346/115243282-0c773b80-a123-11eb-9de7-59e3934a5712.jpg" alt="phoenixnap Bare Metal Cloud"></a>
</p>
