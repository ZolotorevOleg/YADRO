# Kubeadm Role

Role for installing and configuring Kubernetes cluster using kubeadm.

## Description

This role installs kubeadm, initializes the control plane, joins worker nodes, and installs a CNI plugin (calico).

The role is idempotent and safe to run multiple times.

## Dependencies

No external roles or collections are required.

## Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| kubeadm_enable_kubelet | bool | true | Enable kubelet service |
| kubeadm_pod_network_cidr | string | "192.168.0.0/16" | Pod network CIDR |
| kubeadm_kubeconfifg_path | string | /etc/kubernetes/admin.conf | Path to kuberconfig |
| kubeadm_cri_socket | string | "unix:///var/run/crio/crio.sock" | CRI socket |
| kubeadm_install_cni | bool | true | Install CNI plugin |
| kubeadm_cni_url | string | "https://raw.githubusercontent.com/projectcalico/calico/v3.30.2/manifests/calico.yaml" | CNI manifest |

### Tested with Molecule and Ansible.
