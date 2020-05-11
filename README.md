# Ansible - Projects - Contrail

## Usage

Control Juniper's Contrail infrastructure using Ansible.

## Specificities

This project uses custom Ansible components:

| Component                     | Component type            | Description                                          |
|-------------------------------|---------------------------|------------------------------------------------------|
| `plugins/httpapi/contrail.py` | Ansible connection plugin | Ansible interface for Juniper Contrail API           |
| `library/contrail.py`         | Ansible module            | Ansible module to control Juniper Contrail resources |
