# Ansible requires support for both Python 2.6+ and 3.5+
# See here: https://docs.ansible.com/ansible/latest/dev_guide/developing_python_3.html
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from collections import namedtuple
import requests


FQName = namedtuple("FQName", ["domain", "project", "name"])



class Resource:
    def __init__(self, host, fqname, uuid):
        self.host = host
        self.fqname = fqname
        self.uuid = uuid
        print(f'{self.fqname}: {self.uuid}')


class Tungsten:
    def __init__(self, url, token=None):
        self.url = url
        self.token = token
        self.session = requests.Session()

    def resolve_uuid(self, uuid):
        r = self.session.post("{0}/id-to-fqname".format(self.url), json={"uuid": uuid}).json()
        return (r["type"], FQName(*r["fq_name"]))

    def resolve_fqname(self, typename, fqname: FQName):
        return self.session.post("{0}/fqname-to-id".format(self.url), json={
            "type": typename,
            "fq_name": [fqname.domain, fqname.project, fqname.name]
        }).json()

    def get(self, typename=None, fqname=None, uuid=None) -> Resource:
        '''Retrieves a resource from Tungsten API.

        Either `fqname` or `uuid` is required.

        :param typename: Resource typename (e.g. 'virtual-network')
        :param fqname: Resource FQName
        :param uuid: Resource UUID
        '''
        if fqname:
            return Resource(host=self, fqname=fqname, uuid=self.resolve_fqname(typename, fqname))
        elif uuid:
            return Resource(host=self, fqname=self.resolve_uuid(uuid), uuid=uuid)
        else:
            raise Exception(f'Invalid arguments: either fqname or uuid must be provided')



def main():
    host = Tungsten(url="http://172.16.48.31:8082")
    host.get(typename="virtual-network", fqname=FQName("default-domain", "vCenter", "VPCB1"))


if __name__ == "__main__":
    main()
