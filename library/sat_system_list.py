#!/usr/bin/python

# Author: Courtney Campbell
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '2.8',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: sat_system_list
short_description: Returns system list
description:
    - Returns system list
version_added: "2.8"
author:
- Courtney Campbell (@cocampbe)
options:
    url:
        description:
            - The full URL to the RHN/Satellite API.
        required: true
    user:
        description:
            - Satellite login.
        required: true
    password:
        description:
            - Satellite password.
        required: true
    listtype:
        description:
            - returns all systems by default. setting to ood will only return Out Of Date systems.
        choices:
          - all (default)
          - ood
        required: false
'''

EXAMPLES = '''
- sat_system_list:
    url: https://satellite.example.com/rpc/api
    user: sat_user
    password: sat_password
  register: systems

  - debug: msg="{{item}}"
    loop: "{{systems.system_list}}"
'''

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import xmlrpc_client


def get_system_list(client, session):
    system_names = []
    systems = client.system.listSystems(session)
    for system in systems:
        system_names.append(system['name'])
    return system_names

def get_ood_system_list(client, session):
    system_names = []
    systems = client.system.listOutOfDateSystems(session)
    for system in systems:
        system_names.append(system['name'])
    return system_names


def main():

    module = AnsibleModule(
        argument_spec=dict(
            url=dict(type='str', required=True),
            user=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            listtype=dict(type='str', required=False, default='all', choices=['all', 'ood']),
        )
    )

    result = {}
    result['url'] = url = module.params['url']
    result['user'] = user = module.params['user']
    result['listtype'] = listtype = module.params['listtype']
    password = module.params['password']

    # Initialize connection
    client = xmlrpc_client.ServerProxy(url)
    try:
        session = client.auth.login(user, password)
    except Exception as e:
        module.fail_json(msg="Cannot connect to sattelite server: %s " % to_text(e))

    if not session:
        module.fail_json(msg="Cannot connect to sattelite server.")

    # Get system list
    try:
        if listtype == 'ood':
            system_list = get_ood_system_list(client, session)
        else:
            system_list = get_system_list(client, session)
        result['changed'] = True
        result['msg'] = "System list successful."
        result['system_list'] = system_list
        result['count'] = len(system_list)
        module.exit_json(**result)
    except Exception as e:
        result['changed'] = False
        result['msg'] = "Error getting system list."
        module.exit_json(**result)
    finally:
        client.auth.logout(session)


if __name__ == '__main__':
    main()
