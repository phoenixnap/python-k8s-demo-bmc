#!/bin/bash

sudo snap install microk8s --classic --channel=1.17/stable

if ! snap list | grep -q microk8s; then
  echo "Retrying to install microk8s";
  sleep 10
  sudo snap install microk8s --classic --channel=1.17/stable
fi
echo "alias kubectl=microk8s.kubectl" >> ~/.bashrc
exit

