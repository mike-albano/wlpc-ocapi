"""Module used to issue gNMI GetRequests from our sample Target.

Uses Python protobuf generated from gnmi.proto
"""

import sys
import gnmi_pb2
import gnmi_pb2_grpc
import grpc
import json


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

def GetRequest(stub, path):
  """Issue a gNMI GetRequest for the given path."""
  path_list = [gnmi_pb2.PathElem(name=path, key={})]
  paths = gnmi_pb2.Path(elem=path_list)
  # Metadata is User/pass for our example gNMI Target
  response = stub.Get(gnmi_pb2.GetRequest(path=[paths]), metadata=[
      ('username', 'foo'), ('password', 'bar')])
  return response

if __name__ == '__main__':
  stub = SetUpChannel()
  gnmi_response = GetRequest(stub, 'interfaces')
  print(gnmi_response)  #Print as PB
