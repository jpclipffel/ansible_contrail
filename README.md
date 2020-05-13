# Ansible - Projects - Contrail

## Usage

Control Juniper's Contrail infrastructure using Ansible.

## Custom components

This project uses two customs Ansible components:

| Component                     | Component type            | Description                                 | Documentation                                                       |
|-------------------------------|---------------------------|---------------------------------------------|---------------------------------------------------------------------|
| `library/contrail.py`         | Ansible module            | Ansible module for Juniper Contrail         | [User](doc/contrail-module.md)<br>[Dev](doc/contrail-module-dev.md) |
| `plugins/httpapi/contrail.py` | Ansible connection plugin | Ansible HTTPApi plugin for Juniper Contrail | [Dev](doc/contrail-plugin-dev.md)                                   |
