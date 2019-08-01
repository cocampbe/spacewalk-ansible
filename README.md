# satellite-ansible
satellite modules for anibsle

# Examples

```
- sat_system_list:
    url: https://satellite.example.com/rpc/api
    user: sat_user
    password: sat_password
  register: systems
  - debug: msg="{{item}}"
    loop: "{{systems.system_list}}"
```
