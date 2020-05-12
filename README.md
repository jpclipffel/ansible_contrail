# Ansible - Projects - Contrail

## Usage

Control Juniper's Contrail infrastructure using Ansible.

## Custom components

This project uses two custom Ansible components:

| Component                     | Component type            | Description                                          |
|-------------------------------|---------------------------|------------------------------------------------------|
| `library/contrail.py`         | Ansible module            | Ansible module to control Juniper Contrail resources |
| `plugins/httpapi/contrail.py` | Ansible connection plugin | Ansible interface for Juniper Contrail API           |

## `contrail` module usage

### Synopsis

* Use the Juniper's Contrail's REST API.
* Does not support authentication yet.
* Support check mode.

### Requirements

The below requirements are needed on the Ansible controller that executes this module.

* Ansible plugin `httpapi.contrail` 

### Parameters

| Parameter                        | Choices/Defaults                 | Comments                                            |
|----------------------------------|----------------------------------|-----------------------------------------------------|
| **name**<br>*string/required*    |                                  | Contrail's resource name (e.g. `my_vpc`)            |
| **type**<br>*string/required*    |                                  | Contrail's resource type (e.g. `virtual-network`)   |
| **domain**<br>*string/required*  |                                  | Contrail's domain name (e.g. `default-domain`)      |
| **project**<br>*string/required* |                                  | Contrail's project name (e.g. `vCenter`)            |
| **definition**<br>*complex*      |                                  | The resource defnition as specifiec in Contrail API |
| **state**<br>*string/required*   | - present<br>- absent<br>- query | Determine if an object should be created, patched, deleted or queried. When set to `present`, a resource will be created, if it does not already exist. If set to `absent`, an existing resource will be deleted. If set to `present`, an existing resource will be patched, if its attributes differ from those specified using `definition` |

### Examples

```yaml
- name: Query a resource
  register: _contrail_vpc
  contrail:
    name: VPCB1
    type: virtual-network
    domain: default-domain
    project: vCenter
    state: query
  
- name: Print API request status code (integer)
  debug:
    var: _contrail_vpc.status_code

- name: Print API request response (JSON)
  debug:
    var: _contrail_vpc.content
```

### Return values

Common return values are documented [here](https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#common-return-values), the following are the fields unique to this module:

| Key                                 | Returned | Description                                                                                                            |
|-------------------------------------|----------|------------------------------------------------------------------------------------------------------------------------|
| **result**<br>*complex*             | always   | Contrail response                                                                                                      |
| **result.status_code**<br>*integer* | always   | Contrail response code (standard HTTP code)                                                                            |
| **result.content**<br>*json*        | always   | Contrail response content. If `success`, represent if resource definition. Otherwise, represent the error description. |
