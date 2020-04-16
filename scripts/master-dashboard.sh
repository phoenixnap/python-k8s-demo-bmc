#!/bin/bash

sudo microk8s.enable dashboard

sudo microk8s.kubectl -n kube-system patch service kubernetes-dashboard --patch '{"spec": {"type":"NodePort"}}'

token=$(sudo microk8s.kubectl -n kube-system get secret | grep default-token | cut -d " " -f1)
