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
module: sw_system_packages
short_description: spacewalk package module
description:
    - Returns package list.
version_added: "2.8"
author:
- Courtney Campbell (@cocampbe)
options:
    name:
        description:
            - hostname 
        required: true
    url:
        description:
            - The full URL to the Spacewalk API.
        required: true
    user:
        description:
            - spacewalk login.
        required: true
    password:
        description:
            - spacewalk password.
        required: true
    upgradable:
        description:
            - Return upgradable packages.
        type: bool
        required: false
    extra:
        description:
            - Return extra packages.
        type: bool
        required: false
'''

EXAMPLES = '''
- sw_system_packages:
    name: server01
    url: https://spacewalk.example.com/rpc/api
    user: sw_user
    password: sw_password
  register: packages

  - debug: msg="{{item}}"
    loop: "{{packages.packages}}"
'''

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import xmlrpc_client


def get_system_id(client, session, system_name):
    systems = client.system.listSystems(session)
    for system in systems:
        if system['name'] == system_name:
            return system['id']
    return "Not Found"

 
def get_packages(client, session, systemId):
    package_names = []
    packages = client.system.listPackages(session, systemId)
    for package in packages:
        package_names.append(package['name'])
    return package_names


def get_upgradable_packages(client, session, systemId):
    package_names = []
    packages = client.system.listLatestUpgradablePackages(session,systemId)
    for package in packages:
        package_names.append(package['name'])
    return package_names


def get_extra_packages(client, session, systemId):
    package_names = []
    packages = client.system.listExtraPackages(session,systemId)
    for package in packages:
        package_names.append(package['name'])
    return package_names


def main():

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            url=dict(type='str', required=True),
            user=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            upgradable=dict(type='bool', required=False, default=False),
            extra=dict(type='bool', required=False, default=False),
        )
    )

    result = {}
    result['system'] = system = module.params['name']
    result['url'] = url = module.params['url']
    result['user'] = user = module.params['user']
    password = module.params['password']
    result['upgradable'] = upgradable = module.params['upgradable']
    result['extra'] = extra = module.params['extra']

    # Initialize connection
    client = xmlrpc_client.ServerProxy(url)
    try:
        session = client.auth.login(user, password)
    except Exception as e:
        module.fail_json(msg="Cannot connect to spacewalk server: %s " % to_text(e))

    if not session:
        module.fail_json(msg="Cannot connect to spacewalk server.")

    # Get system list
    try:
        systemId = get_system_id(client, session, system)
        if upgradable:
            package_list = get_upgradable_packages(client, session, systemId)
        elif extra:
            package_list = get_extra_packages(client, session, systemId)
        else:
            package_list = get_packages(client, session, systemId)
        result['packages'] = package_list
        result['changed'] = True
        result['count'] = len(package_list)
        module.exit_json(**result)
    except Exception as e:
        result['changed'] = False
        result['msg'] = str(e)
        module.fail_json(**result)
    finally:
        client.auth.logout(session)


if __name__ == '__main__':
    main()
