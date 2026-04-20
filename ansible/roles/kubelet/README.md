# Kubelet Role

Role for installing and configuring kubelet on Kubernetes nodes.

## Description

This role installs kubelet and optionally kubectl, enables the kubelet service, and ensures package versions are held.

## Dependencies

No external roles or collections are required.

## Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| kubelet_enable_service | bool | true | Enable kubelet |
| kubelet_start_service | bool | true | Start kubelet |
| kubelet_install_kubectl | bool | false | Install kubectl |
| kubelet_hold_packages | bool | true | Hold packages |

### Tested with Molecule and Ansible.
