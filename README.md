# spacewalk-ansible
spacewalk modules for anibsle

# Examples

```
- sw_system_list:
    url: https://spacewalk.example.com/rpc/api
    user: sw_admin
    password: sw_pass
  register: systems
  - debug: msg="{{item}}"
    loop: "{{systems.system_list}}"

- sw_system_packages:
    name: server01
    url: https://spacewalk.example.com/rpc/api
    user: sw_admin
    password: my_pass
  register: packages

- name: get upgradable pacakges
  sw_system_packages:
    name: server01
    url: https://spacewalk.example.com/rpc/api
    user: sw_admin
    password: my_pass
    upgradable: yes
  register: packages
```
