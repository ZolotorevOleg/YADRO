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

## Testing

Molecule tests use a separate test inventory file:

- `inventory/test-hosts.ini`

This file can contain the same hosts as the main inventory, but it is isolated from the production playbook configuration.

To run Molecule tests:

```bash
cd roles/crio && molecule test
cd ../kubelet && molecule test
cd ../kubeadm && molecule test
```

For local testing, replace host addresses and SSH users in `inventory/test-hosts.ini` with your own test machines.
If needed, adjust variables in `inventory/group_vars/`.
