#!/bin/bash

sudo snap install kubectl --classic
mkdir -p ~/.kube
export KUBECONFIG=~/.kube/config
if ! snap list | grep -q kubectl; then
  echo "Retrying to install kubectl";
  sleep 10
  sudo snap install kubectl --classic
fi
exit

