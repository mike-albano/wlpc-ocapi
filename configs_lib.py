"""Configuration module for Mist/Arista provisioning.

One 'could' populate a list of APs from a given heatmap for multi-ap
configuration.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from absl import logging
from absl import flags
import constants
import gnmi_lib
import six
import sys
import json
import pyangbind.lib.pybindJSON as pybindJSON
from ap_manager_bindings import openconfig_ap_manager
from access_points_bindings import openconfig_access_points

ap_manager_configs = openconfig_ap_manager()
access_point_configs = openconfig_access_points()

FLAGS = flags.FLAGS

class Error(Exception):
  """Module-level Exception class."""


def GnmiSetUp(ap):
  """Set up gNMI channel for each AP.

  Args:
    ap: AP Class object.
  """
  if ap.targetport == '443':  # Target is ap-mgr.
    root_cert=six.moves.builtins.open('mist-ca.cert.pem', 'rb').read()
    creds = gnmi_lib.CreateCreds(ap.targetip, ap.targetport, root_cert)
    ap.stub = gnmi_lib.CreateStub(creds, ap.targetip, ap.targetport,
                                  'openconfig.mist.com')
  elif ap.targetport == '8080':  # Targt is AP
    creds = gnmi_lib.CreateCreds(ap.targetip, ap.targetport, None)
    ap.stub = gnmi_lib.CreateStub(creds, ap.targetip, ap.targetport,
                                  'openconfig.mojonetworks.com')
  elif ap.targetport == '10161':  # Target is ap-mgr.
    creds = gnmi_lib.CreateCreds(ap.targetip, ap.targetport, root_cert)
    ap.stub = gnmi_lib.CreateStub(creds, ap.targetip, ap.targetport,
                                  'openconfig.cisco.com')
  elif ap.targetport == '10181':  # Targt is AP
    creds = gnmi_lib.CreateCreds(ap.targetip, ap.targetport, root_cert)
    ap.stub = gnmi_lib.CreateStub(creds, ap.targetip, ap.targetport,
                                    'openconfig.arubanetworks.com')


def Provision(ap):
  """Triggers the provisioning workflow.

  Args:
    ap: AP Class object.

  This populates the conig object (from PyangBind, from YANG model) for day-0
  provisioning.
  """
  paths = gnmi_lib.ParsePath(gnmi_lib.PathNames((
    '/provision-aps/provision-ap[mac=%s]/' % ap.mac)))
  provision_apconfigs = ap_manager_configs.provision_aps.provision_ap
  day0 = provision_apconfigs.add(ap.mac)
  day0.config.mac = ap.mac
  day0.config.hostname = ap.ap_name
  day0.config.country_code = 'US'
  json_value = json.loads(pybindJSON.dumps(day0, mode='ietf', indent=2))
  if FLAGS.dry_run:
    print('Here\'s the JSON that was created, for sending to the Target:')
    print('*'*25, '\n\n', json.dumps(json_value, indent=2),'\n\n', '*'*25)
    print('JSON written as dry_run_provision.json')
    f = six.moves.builtins.open('dry_run_provision.json', 'w')
    f.write(json.dumps(json_value, indent=2) + '\n')
    sys.exit()
  else:
    r = gnmi_lib.Set(ap.stub, paths, ap.targetuser, ap.targetpass, json_value, 'update')
    print('provisioning succesfull, with the following gNMI SetResponse:\n', r)


def ConfigPhyMac(ap, student_ssids):
  """Triggers the configuration of PHY and MAC layer.

  Args:
    ap: AP Class object.
    student_ssids: (list) SSIDs to configure on the AP.

  This populates the conig object (from PyangBind, from YANG model) for day-1+
  configuration.
  """
  paths = gnmi_lib.ParsePath(gnmi_lib.PathNames((
    '/access-points/access-point[hostname=%s]/' % ap.ap_name)))
  ap_configs = access_point_configs.access_points.access_point
  ap_configs.add(ap.ap_name)
  open_ssid = ap_configs[ap.ap_name].ssids.ssid.add(ap.openssid)
  open_ssid.config.name = ap.openssid
  open_ssid.config.enabled = True
  open_ssid.config.hidden = False
  open_ssid.config.operating_frequency = 'FREQ_5GHZ'
  #open_ssid.config.basic_data_rates = ['RATE_36MB', 'RATE_48MB', 'RATE_54MB']
  #open_ssid.config.supported_data_rates = ['RATE_36MB', 'RATE_48MB', 'RATE_54MB']
  open_ssid.config.opmode = 'OPEN'
  open_ssid.wmm.config.trust_dscp = True
  psk_ssid = ap_configs[ap.ap_name].ssids.ssid.add(ap.pskssid)
  psk_ssid.config.enabled = True
  psk_ssid.config.name = ap.pskssid
  psk_ssid.config.hidden = False
  psk_ssid.config.operating_frequency = 'FREQ_2_5_GHZ'
  #psk_ssid.config.basic_data_rates = ['RATE_36MB', 'RATE_48MB', 'RATE_54MB']
  #psk_ssid.config.supported_data_rates = ['RATE_36MB', 'RATE_48MB', 'RATE_54MB']
  psk_ssid.config.opmode = 'WPA2_PERSONAL'
  psk_ssid.config.wpa2_psk = 'testing123'
  psk_ssid.wmm.config.trust_dscp = True
  # PHY Layer stuff.
  fiveg = ap_configs[ap.ap_name].radios.radio.add(0)
  fiveg.config.id = 0
  fiveg.config.operating_frequency = 'FREQ_5GHZ'
  fiveg.config.enabled = True
  fiveg.config.dca = False
  fiveg.config.transmit_power = 3
  fiveg.config.channel_width = 20
  fiveg.config.channel = 165
  twog = ap_configs[ap.ap_name].radios.radio.add(1)
  twog.config.id = 1
  twog.config.operating_frequency = 'FREQ_2GHZ'
  twog.config.enabled = True
  twog.config.dca = False
  twog.config.transmit_power = 3
  twog.config.channel_width = 20
  twog.config.channel = 6
  json_value = _int_fixer(json.loads(pybindJSON.dumps(
    access_point_configs, mode='ietf', indent=2))['openconfig-access-points:access-points']['access-point'][0])
  if FLAGS.dry_run:
    print('Here\'s the JSON that was created, for sending to the Target:')
    print('*'*25, '\n\n', json.dumps(json_value, indent=2),'\n\n', '*'*25)
    print('JSON written as dry_run_configs.json')
    f = six.moves.builtins.open('dry_run_configs.json', 'w')
    f.write(json.dumps(json_value, indent=2) + '\n')
    sys.exit()
  else:
    r = gnmi_lib.Set(ap.stub, paths, ap.targetuser, ap.targetpass, json_value, 'update')
    print('Configuration succesfull, with the following gNMI SetResponse:\n', r)
    return json.dumps(json_value)


def _int_fixer(js):
  """Small helper to fix integer-as-string PyangBind bug."""
  for radio in js['radios']['radio']:
    if radio['id'] == "0":
      radio['id'] = 0
    if radio['id'] == "1":
      radio['id'] = 1
  return js
