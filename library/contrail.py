ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: contrail

short_description: Interact with Juniper Contrail via REST API

version_added: "2.9"

description:
    - "Interact with Juniper Contrail via REST API"

options:
    name:
        description:
            - Resource name
        required: true
        type: 'str'
    type:
        description:
            - Resource type (e.g. virtual-network)
        required: true
        type: str
    state:
        description:
            - Expected resource state
        required: true
        choices:
            - present
            - absent
            - query
        type: str
    domain:
        description:
            - Domain name (e.g. default-domain)
        required: true
        type: str
    project:
        description:
            - Project name (e.g. vCenter)
        required: true
        type: str
    definition:
        description:
            - Resource definition (REST API payload)
        required: false
        type: dict

author:
    - Jean-Philippe Clipffel (@jpclipffel)
'''

EXAMPLES = '''
# Pass in a message
- name: Get a resource
  contrail:
    type: virtual-network
    domain: default-domain
    project: vCenter
    name: VPCB1
'''

RETURN = '''
msg:
    description: Action status
    type: str
    returned: always
api:
    description: Contrail API request and response
    type: complex
    returned: always
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection


class Result:
    '''Generic Contrail API result.

    Any request made to the API (i.e. using `send_request`) **should** returns a :class:`Result` instance.
    '''
    def __init__(self, changed=False, failed=False, msg="", method="", path="", request={}, response={}, status_code=-1):
        self.changed = changed
        self.failed = failed
        self.msg = msg
        # ---
        self.method = method
        self.path = path
        self.request = request
        self.response = response
        self.status_code = status_code
    
    def to_dict(self):
        '''Transforms the :class:`Result` to a `dict` object suitable for Ansible.
        '''
        return {
            "changed": self.changed,
            "failed": self.failed,
            "msg": self.msg,
            "api": {
                "method": self.method,
                "path": self.path,
                "request": self.request,
                "response": self.response,
                "status_code": self.status_code
            }
        }


class ContrailError(Exception):
    '''Generic Contrail API error.

    This exception simply wraps a :class:`Result`.
    '''
    def __init__(self, result):
        self.result = result


class Resource:
    '''Generic Contrail resource interface.

    One **can't** use a :class:`Resource` directly: a derivied class, such as
    :class:`VirtualNetwork` must be used instead,
    '''

    # Resource properties, overide by :class:`Resource`'s derived classes.
    type = ""           # string; The resource type name (e.g. 'virtual-network')
    path_get = ""       # string; API path to 'GET' the resource 
    path_put = ""       # string; API path to 'PUT' to the resource
    path_post = ""      # string; API path to 'POST' to the resource
    parent_type = ""    # string; Resource parent type name (e.g. 'project')

    def __init__(self, contrail, name, project, domain):
        '''Initializes the instance.

        :param Contrail contrail: :class:`Contrail` instance
        :param str name: Resource name (== display name)
        :param str project: Resource project name
        :param domain: Resource domain name
        '''
        self.contrail = contrail
        self.name = name
        self.project = project
        self.domain = domain
        # ---
        self._uuid = None
        self._definition = None
    
    @property
    def uuid(self):
        '''Returns the resource UUID or `None` if the resource does not exists.

        :rtype: str, None
        :raise: ContrailError
        '''
        method, path = "POST", "/fqname-to-id"
        request, content, status_code = {}, {}, -1
        # ---
        try:
            if not self._uuid:
                request = {"type": self.type, "fq_name": [self.domain, self.project, self.name]}
                status_code, content = self.contrail.connection.send_request(method, path, request)
                if status_code in [200, ] and "uuid" in content:
                    self._uuid = content["uuid"]
            return self._uuid
        except Exception as error:
            raise ContrailError(Result(
                failed=True, msg='Exception: {0}'.format(str(error)), 
                method=method, path=path, request=request, response=content, status_code=status_code))
    
    @property
    def definition(self):
        '''Returns the resource definition or `{}` (an empty :class:`dict`) if resource does not exists.

        :rtype: dict
        :raise: ContrailError
        '''
        method, path = "GET", "/{0}/{1}".format(self.path_get, self.uuid)
        request, content, status_code = {}, {}, -1
        # ---
        try:
            if not self._definition:
                status_code, content = self.contrail.connection.send_request(method, path)
                if status_code in [200, ]:
                    self._definition = content
            return self._definition
        except Exception as error:
            raise ContrailError(Result(
                failed=True, msg='Exception: {0}'.format(str(error)), 
                method=method, path=path, request=request, response=content, status_code=status_code))
    
    @property
    def exists(self):
        '''Returns `True` is the resource exists (i.e. has an UUID), `False` otherwise.

        :rtype: Bool
        '''
        if self.uuid:
            return True
        return None

    def apply(self, definition):
        '''Creates or update the resource.

        If the resource already exists, a 'PUT' call is performed.
        If the resource doesn't exists, a 'POST' call is performed.

        :param dict definition: Resource definition (API payload)
        :rtype: Result
        :raise: ContrailError
        '''
        method, path = "", ""
        _definition, content, status_code = {}, {}, -1
        # ---
        try:
            _definition = {self.type: {
                "parent_type": self.parent_type,
                "fq_name": [ self.domain, self.project, self.name ]
            }}
            _definition[self.type].update(definition)
            # ---
            if self.exists:
                method, path = "PUT", "/{0}/{1}".format(self.path_put, self.uuid)
            else:
                method, path = "POST", "/{0}".format(self.path_post)
            # ---
            status_code, content = self.contrail.connection.send_request(method, path, _definition)
            # ---
            if status_code in [200, ]:
                return Result(
                    changed=True, msg="Resource updated",
                    method=method, path=path, request=_definition, response=content, status_code=status_code)
            else:
                raise ContrailError(Result(
                    failed=True, msg="Failed to update resource", 
                    method=method, path=path, request=_definition, response=content, status_code=status_code))
        except ContrailError as error:
            raise error
        except Exception as error:
            raise ContrailError(Result())

    def delete(self):
        '''Deletes the resource.

        If the resource exists, a 'DELETE' call is performed.
        If the resource doesn't exists, nothing is done.

        :rtype: Result
        :raise: ContrailError
        '''
        method, path = "DELETE", "/{0}/{1}".format(self.path_put, self.uuid)
        _definition, status_code = {}, -1
        # ---
        try:
            if self.exists:
                msg = "Resource deleted"
                status_code, _ = self.contrail.connection.send_request(method, path)
            else:
                msg = "Resource does not exists"
            return Result(
                changed=False, msg=msg, 
                method=method, path=path, status_code=status_code)
        except ContrailError as error:
            raise error
        except Exception as error:
            raise ContrailError(Result(
                failed=True, msg='Exception: {0}'.format(str(error)),
                method=method, path=path, status_code=status_code))


class VirtualNetwork(Resource):
    '''Contrail API object 'virtual-network'
    '''
    type = "virtual-network"
    path_get = "virtual-network"
    path_put = "virtual-network"
    path_post = "virtual-networks"
    parent_type = "project"


class Contrail:
    '''Interfaces with Contrail API (high-level functions).

    :attr resources_map: Mapping between resources type name and classes.
    '''

    resources_map = {
        "virtual-network": VirtualNetwork
    }

    def __init__(self, module, connection):
        '''Initializes instance.

        :param object module: Ansible module instance
        :param object connection: Ansible connection plugin interface
        '''
        self.module = module
        self.connection = connection

    def resource(self, type, name, project, domain):
        '''Returns the requested resource.

        :param str type: Resource type name (e.g. 'virtual-network')
        :param str name: Resource name
        :param str project: Resource project
        :param str domain: Resource domain

        :return: A new resource instance
        :rtype: Resource
        :raise: ContrailError
        '''
        if not type in self.resources_map:
            raise ContrailError(Result(False, "failure", "Unknown resource type: {0}".format(type)))
        return self.resources_map[type](self, name, project, domain)

    def state_query(self, type, name, project, domain):
        '''Query a resource.

        :param str type: Resource type name (e.g. 'virtual-network')
        :param str name: Resource name
        :param str project: Resource project
        :param str domain: Resource domain

        :return: A new resource instance
        :rtype: Result
        :raise: ContrailError
        '''
        resource = self.resource(type, name, project, domain)
        if resource.exists:
            return Result(msg="Resource queried", response=resource.definition)
        else:
            return Result(failed=True, msg="Resource does not exists")

    def state_present(self, type, name, project, domain, definition):
        '''Creates or updates a resource.

        :param str type: Resource type name (e.g. 'virtual-network')
        :param str name: Resource name
        :param str project: Resource project
        :param str domain: Resource domain
        :param definition: Resource definition (API payload)

        :return: A new resource instance
        :rtype: Result
        :raise: ContrailError
        '''
        try:
            resource = self.resource(type, name, project, domain)
            return resource.apply(definition)
        except ContrailError as error:
            raise error

    def state_absent(self, type, name, project, domain):
        '''Removes a resource.

        :param str type: Resource type name (e.g. 'virtual-network')
        :param str name: Resource name
        :param str project: Resource project
        :param str domain: Resource domain

        :return: A new resource instance
        :rtype: Result
        :raise: ContrailError
        '''
        try:
            resource = self.resource(type, name, project, domain)
            return resource.delete()
        except ContrailError as error:
            raise error


def run_module():
    '''Ansible module entry point.
    '''
    # Ansible module arguments
    module_args = dict(
        name=dict(type=str, required=True),
        type=dict(type="str", required=True),
        state=dict(type="str", required=True),
        domain=dict(type="str", required=True),
        project=dict(type="str", required=True),
        definition=dict(type="dict", required=False, default={}))
    # Initializes module, connection and API helper
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    connection = Connection(module._socket_path)
    contrail = Contrail(module, connection)
    # Wraps module parameters
    resource_state = module.params["state"]
    resource_name = module.params["name"]
    resource_type = module.params["type"]
    resource_domain = module.params["domain"]
    resource_project = module.params["project"]
    resource_definition = module.params["definition"]
    # Run module
    try:
        # Run module in 'query' mode (gather info)
        if resource_state in ["query", "status", ]:
            result = contrail.state_query(resource_type, resource_name, resource_project, resource_domain)
        # Run module in 'present' mode (may create or update resource(s))
        elif resource_state in ["present", ]:
            result = contrail.state_present(resource_type, resource_name, resource_project, resource_domain, resource_definition)
        # Run module in 'absent' mode (may deletes resource(s))
        elif resource_state in ["absent", ]:
            result = contrail.state_absent(resource_type, resource_name, resource_project, resource_domain)
        # Invalid state
        else:
            result = Result(failed=True, msg="Invalid module state: {0}".format(resource_state))
    except ContrailError as error:
        result = error.result
    # Exit
    if result.failed:
        module.fail_json(**result.to_dict())
    else:
        module.exit_json(**result.to_dict())


def main():
    run_module()


if __name__ == '__main__':
    main()
