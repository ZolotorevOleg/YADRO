# CRI-O Role

Role for installing and configuring CRI-O (Container Runtime Interface) on Kubernetes nodes.

## Description

This role installs CRI-O (version >= 1.32), configures repositories, disables swap, and ensures the CRI-O service is enabled and running.

## Dependencies

No external roles or collections are required.

## Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| crio_kubernetes_version | string | "v1.32" | Kubernetes repo version |
| crio_version | string | "v1.32" | CRI-O version |
| crio_enable_service | bool | true | Enable CRI-O service |
| crio_start_service | bool | true | Start CRI-O service |
| crio_disable_swap | bool | true | Disable swap |
| proxy_enabled | bool | false | Enable proxy |
| proxy_host | string | "" | Proxy host |
| proxy_port | int | 3128 | Proxy port |


### Tested with Molecule and Ansible.
