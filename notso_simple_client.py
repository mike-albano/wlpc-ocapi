"""Module used to issue gNMI GetRequests from our sample Target.

Uses Python protobuf generated from gnmi.proto
"""

import sys
sys.path.append('/home/user/client_app')  # For importing gnmi protos
import gnmi_pb2
import gnmi_pb2_grpc
import grpc
import json
import time
import pyangbind.lib.pybindJSON as pybindJSON
from pyangbind.lib.serialise import pybindJSONDecoder
from interface_bindings import openconfig_interface
from influxdb import InfluxDBClient

configs = openconfig_interface()

def CreateConfigs():
  int_conf = configs.interfaces
  int_conf.config.enabled = True
  return int_conf


def SetUpChannel():
  """Set up the gNMI RPC."""
  wdir = '/home/user/'
  # Specify the credentials in use.
  creds = grpc.ssl_channel_credentials(root_certificates=open(wdir +
      'client-ca.crt').read(), private_key=open(wdir +
          'client.key').read(), certificate_chain=open(wdir +
              'client.crt').read())
  # Assgin the gRPC channel to our gNMI Target.
  channel = grpc.secure_channel('www.example.com:10161', creds)
  stub = gnmi_pb2_grpc.gNMIStub(channel)
  return stub

def GetRequest(stub, path_list):
  """Issue a gNMI GetRequest for the given path."""
  paths = gnmi_pb2.Path(elem=path_list)
  # Metadata is User/pass for our example gNMI Target
  response = stub.Get(gnmi_pb2.GetRequest(path=[paths]), metadata=[
      ('username', 'foo'), ('password', 'bar')])
  return response

if __name__ == '__main__':
  all_configs = CreateConfigs()
  stub = SetUpChannel()
  path_list = [gnmi_pb2.PathElem(name='interfaces', key={}),
               gnmi_pb2.PathElem(name='config', key={})]
  gnmi_response = GetRequest(stub, path_list)
  js_response = json.loads(gnmi_response.notification[0].update[0].val.json_val)
  pybindJSONDecoder.load_json(js_response, None, None, obj=configs.interfaces.config)
  print(pybindJSON.dumps(configs, indent=2))
