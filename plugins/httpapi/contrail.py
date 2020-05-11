from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
author:
    - Jean-Philippe Clipffel (@jpclipffel)
httpapi : contrail
short_description: Httpapi Plugin for Juniper Contrail REST API
description:
  - This httpapi plugin provides methods to connect to Juniper Contrail via REST API
version_added: "2.9"

'''

import json

from ansible.errors import AnsibleConnectionFailure
from ansible.plugins.httpapi import HttpApiBase
from ansible.module_utils.basic import to_text
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.six.moves.urllib.error import HTTPError


BASE_HEADERS = {
    "Content-Type": "application/json;charset=UTF-8"
}


class HttpApi(HttpApiBase):
    def __init__(self, connection):
        super(HttpApi, self).__init__(connection)

    def send_request(self, request_method, path, data={}):
        '''Prepares, sends and control Contrail API requests.

        :param str request_method: HTTP method
        :param str path: API path
        :param dict data: Request data, serializable as JSON

        :return: A tuple as (status_code: int, content: dict)
        :rtype: tuple
        '''
        try:
            response, response_data = self.connection.send(path, json.dumps(data), method=request_method, headers=BASE_HEADERS)
            if response.getcode() in [200, ]:
                return response.getcode(), json.loads(to_text(response_data.getvalue()))
            else:
                return response.getcode(), {"message": to_text(response_data.getvalue())}
        except AnsibleConnectionFailure as error:
            if to_text('401') in to_text(error):
                return 401, 'Authentication failure'
        except HTTPError as error:
            error = json.loads(error.read())
            return error.code, error


