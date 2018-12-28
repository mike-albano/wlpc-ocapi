"""Module used to generate configuration blobs for Interfaces.

Uses Python bindings generated from openconfig-interfaces.yang
"""

import pyangbind.lib.pybindJSON as pybindJSON
from interface_bindings import openconfig_interface

configs = openconfig_interface()

def CreateConfigs():
  int_conf = configs.interfaces
  int_conf.config.enabled = True
  return int_conf

if __name__ == '__main__':
  all_configs = CreateConfigs()
  print(pybindJSON.dumps(all_configs, indent=2))
