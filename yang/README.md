# YANG Handler 

### Validating YANG changes

- `pyang -f yin`
- Install into sysrepod
  - `sysrepoctl --install --yang=brewerslab-types.yang`
  - sysrepoctl --install --yang=brewerslab-teststub.yang
- netconf-console --user netconf --password netconf --port 830 --get-schema brewerslab-types

