"""Python3 library used for interacting with network elements using gNMI.

This library used for Get and SetRequests using gNMI.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import json
import re
import ssl
import sys
sys.path.insert(0, './gnmi/proto/gnmi_ext/')
import gnmi_pb2
import gnmi_pb2_grpc


_RE_PATH_COMPONENT = re.compile(r'''
^
(?P<pname>[^[]+)  # gNMI path name
(\[(?P<key>\w+)   # gNMI path key
=
(?P<value>.*)    # gNMI path value
\])?$
''', re.VERBOSE)


class Error(Exception):
  """Module-level Exception class."""


class XpathError(Error):
  """Error parsing xpath provided."""


def PathNames(xpath):
  """Parses the xpath names.

  This takes an input string and converts it to a list of gNMI Path names. Those
  are later turned into a gNMI Path Class object for use in the Get/SetRequests.
  Args:
    xpath: (str) xpath formatted path.

  Returns:
    list of gNMI path names.
  """
  if not xpath or xpath == '/':  # A blank xpath was provided at CLI.
    return []
  return xpath.strip().strip('/').split('/')  # Remove leading and trailing '/'.


def ParsePath(p_names):
  """Parses a list of path names for path keys.

  Args:
    p_names: (list) of path elements, which may include keys.

  Returns:
    a gnmi_pb2.Path object representing gNMI path elements.

  Raises:
    XpathError: Unabled to parse the xpath provided.
  """
  gnmi_elems = []
  for word in p_names:
    word_search = _RE_PATH_COMPONENT.search(word)
    if not word_search:  # Invalid path specified.
      raise XpathError('xpath component parse error: %s' % word)
    if word_search.group('key') is not None:  # A path key was provided.
      gnmi_elems.append(gnmi_pb2.PathElem(name=word_search.group(
          'pname'), key={word_search.group('key'): word_search.group('value')}))
    else:
      gnmi_elems.append(gnmi_pb2.PathElem(name=word, key={}))
  return gnmi_pb2.Path(elem=gnmi_elems)


def CreateCreds(target, port, get_cert, root_cert, cert_chain, private_key):
  """Define credentials used in gNMI Requests.

  Args:
    target: (str) gNMI Target.
    port: (str) gNMI Target IP port.
    get_cert: (str) Certificate should be obtained from Target for gRPC channel.
    root_cert: (str) Root certificate to use in the gRPC channel.
    cert_chain: (str) Certificate chain to use in the gRPC channel.
    private_key: (str) Private key to use in the gRPC channel.

  Returns:
    a gRPC.ssl_channel_credentials object.
  """
  if get_cert:
    print('Obtaining certificate from Target')
    rcert = ssl.get_server_certificate((target, port)).encode('utf-8')
    return gnmi_pb2_grpc.grpc.ssl_channel_credentials(
        root_certificates=rcert, private_key=private_key,
        certificate_chain=cert_chain)
  return gnmi_pb2_grpc.grpc.ssl_channel_credentials(
    root_certificates=root_cert, private_key=private_key,
    certificate_chain=cert_chain)


def CreateStub(creds, target, port, host_override):
  """Creates a gNMI Stub.

  Args:
    creds: (object) of gNMI Credentials class used to build the secure channel.
    target: (str) gNMI Target.
    port: (str) gNMI Target IP port.
    host_override: (str) Hostname being overridden for Cert check.

  Returns:
    a gnmi_pb2_grpc object representing a gNMI Stub.
  """
  if host_override:
    channel = gnmi_pb2_grpc.grpc.secure_channel(target + ':' + port, creds, ((
        'grpc.ssl_target_name_override', host_override,),))
  else:
    channel = gnmi_pb2_grpc.grpc.secure_channel(target + ':' + port, creds)
  return gnmi_pb2_grpc.gNMIStub(channel)


def Get(stub, paths, username, password):
  """Create a gNMI GetRequest.

  Args:
    stub: (class) gNMI Stub used to build the secure channel.
    paths: gNMI Path
    username: (str) Username used when building the channel.
    password: (str) Password used when building the channel.

  Returns:
    a gnmi_pb2.GetResponse object representing a gNMI GetResponse.
  """
  if username and password:  # User/pass supplied for Authentication.
    return stub.Get(
        gnmi_pb2.GetRequest(path=[paths], encoding='JSON_IETF'),
        metadata=[('username', username), ('password', password)])
  return stub.Get(gnmi_pb2.GetRequest(path=[paths], encoding='JSON_IETF'))


def Set(stub, paths, username, password, json_value, set_type):
  """Create a gNMI SetRequest.

  Args:
    stub: (class) gNMI Stub used to build the secure channel.
    paths: gNMI Path.
    username: (str) Username used when building the channel.
    password: (str) Password used when building the channel.
    json_value: (str) JSON_IETF Value or file.
    set_type: (str) Type of gNMI SetRequest to build.
  Returns:
    set_request: (class) gNMI SetRequest.
  """
  val = gnmi_pb2.TypedValue()
  val.json_ietf_val = json.dumps(json_value)
  path_val = gnmi_pb2.Update(path=paths, val=val,)
  if set_type == 'update':
    return stub.Set(gnmi_pb2.SetRequest(update=[path_val]), metadata=[
        ('username', username), ('password', password)])
  elif set_type == 'replace':
    return stub.Set(gnmi_pb2.SetRequest(replace=[path_val]), metadata=[
        ('username', username), ('password', password)])
  elif set_type == 'delete':
    return stub.Set(gnmi_pb2.SetRequest(prefix=paths), metadata=[
        ('username', username), ('password', password)])
