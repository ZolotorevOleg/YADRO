# Kubernetes Cluster Deployment with Ansible

## Description

This project provides a fully automated setup of a Kubernetes cluster using Ansible.

It includes roles for installing:
- CRI-O (container runtime)
- kubelet (node agent)
- kubeadm (cluster bootstrap tool)

The cluster consists of:
- 1 control plane node
- 2 worker nodes

All roles are idempotent and tested with Molecule.

Proxy credentials are stored securely using Ansible Vault.  
The proxy login and password are not hardcoded in roles and are loaded from encrypted variables.

---

## Project Structure

```text
ansible/
├── inventory/
│   ├── hosts.ini
│   └── group_vars/
├── playbooks/
│   └── site.yml
└── roles/
    ├── crio/
    ├── kubelet/
    └── kubeadm/
