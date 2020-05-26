# Ansible - Projects - Contrail

## Usage

Control Juniper's Contrail infrastructure using Ansible.

## Custom components

This project uses two customs Ansible components:

| Component                     | Component type            | Description                                 | Documentation                                                       |
|-------------------------------|---------------------------|---------------------------------------------|---------------------------------------------------------------------|
| `library/contrail.py`         | Ansible module            | Ansible module for Juniper Contrail         | [User](doc/contrail-module.md)<br>[Dev](doc/contrail-module-dev.md) |
| `plugins/httpapi/contrail.py` | Ansible connection plugin | Ansible HTTPApi plugin for Juniper Contrail | [Dev](doc/contrail-plugin-dev.md)                                   |

## To do

The Ansible module and plugin are still a work in progress.

- [x] Basic connection to Contrail from Ansible
- [ ] Authentication support
- [x] State support: `query`
- [x] State support: `present` (resource creation)
- [x] State support: `present` (resource update)
- [x] State support: `absent`
- [x] Resource support: `virtual-network`
- [ ] Resource support: all other required resources (e.g. `IPAM`, `subnet`, etc.)

### Documentation

- [x] Module documentation for users
- [x] Module documentation for dev
- [ ] Plugin documentation for dev
