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
status_code:
    description: Contrail API request status code
    type: int
    returned: always
content:
    description: Contrail API request content
    type: dict
    returned: always
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection


class Contrail:
    def __init__(self, connection):
        self.connection = connection
    
    def get_resource(self, type, name, project, domain):
        status_code, content = self.get_resource_uuid(type, name, project, domain)
        if status_code in [200, ] and "uuid" in content:
            return self.connection.send_request("GET", "/{0}/{1}".format(type, content["uuid"]))
        return status_code, content

    def get_resource_fqname(self, uuid):
        '''Returns a resource fq_name fields from it's uuid.

        :return: A tuple as (status_code: int, content: dict)
        :rtype: tuple
        '''
        return self.connection.send_request("POST", "/id-to-fqname", {"uuid": uuid})
        
    
    def get_resource_uuid(self, type, name, project, domain):
        '''Returns a resource uuid from it's fq_name fields.

        :return: A tuple as (status_code: int, content: dict)
        :rtype: tuple
        '''
        return self.connection.send_request("POST", "/fqname-to-id", {"type": type, "fq_name": [domain, project, name]})
        

def run_module():
    # Ansible module arguments
    module_args = dict(
        name=dict(type=str, required=True),
        type=dict(type="str", required=True),
        state=dict(type="str", required=True),
        domain=dict(type="str", required=True),
        project=dict(type="str", required=True),
        definition=dict(type="dict", required=False, default={}))

    # Initializes module run results
    result = dict(changed=False, msg="", status_code=0, content={})

    # Initializes module, connection and API helper
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    connection = Connection(module._socket_path)
    contrail = Contrail(connection)

    # Wraps module parameters
    resource_state = module.params["state"]
    resource_name = module.params["name"]
    resource_type = module.params["type"]
    resource_domain = module.params["domain"]
    resource_project = module.params["project"]
    resource_definition = module.params["definition"]
    
    # Run module in check mode
    if module.check_mode:
        module.exit_json(**result)

    # Run module in 'query' mode (gather info)
    elif resource_state in ["query", "status", ]:
        status_code, content = contrail.get_resource(resource_type, resource_name, resource_project, resource_domain)

    # Run module in 'present' mode (may create or update resource(s))
    elif resource_state in ["present", ]:
        result["response"] = ""
        result["changed"]  = True

    # Run module in 'absent' mode (may delete resource(s))
    elif resource_state in ["absent", ]:
        result["response"] = ""
        result["changed"]  = True

    # Set module run results and exit
    result["status_code"], result["content"] = status_code, content
    if status_code not in [200, ]:
        result["msg"] = "Failed request"
        module.fail_json(**result)
    result["msg"] = "Successful request"
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
