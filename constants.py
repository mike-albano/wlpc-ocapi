"""Constants file for WLPC gnmicli.

This file stores constants used by gnmicli and related libraries.
"""

import re


PHY_SEARCH = re.compile(
    r'(?P<ap_name>\w\d+-\d\d+)(:)(?P<five_tx_power>[0-9]+)(:)(?P<five_chan_'
    'width>0|20|40|80|160)(:)?(?P<five_channel>0|36|40|44|48|52|56|60|64|100|'
    '104|108|112|116|120|124|128|132|136|140|144|149|153|157|161|165)?(:)'
    '(?P<two_tx_power>[0-9]+)(:)(?P<two_chan_width>0|20|40|80|160)(:)'
    '(?P<two_channel>14|13|12|11|10|9|8|7|6|5|4|3|2|1|0)', re.IGNORECASE)
VENDOR_OUI_DATA = {'mist': ['5c:5b:35'], 'arista': ['30:b6:2d', '88:b1:e1',
'e4:d1:24', '00:11:74'], 'cisco': ['00:01:42'], 'aruba':
                   ['80:8d:b7', '38:17:c3', '24:f2:7f', '20:a6:cd', '44:48:c1',
                    'c8:b5:ad', '34:fc:b9', 'a8:bd:27', 'b4:5d:50', '20:4c:03',
                    '70:3a:0e', 'f0:5c:19', '84:d4:7e', '40:e3:d6', '04:bd:88',
                    '94:b4:0f', 'ac:a3:1e', '18:64:72', '9c:1c:12', '24:de:c6',
                    '6c:f3:7f', 'd8:c7:c8', '00:24:6c', '00:1a:1e', '00:0b:86',
                    'b0:b8:67', '90:4c:81']}
GNMI_TARGETPORTS = {'mist': '443', 'arista': '8080', 'cisco': '10161', 'aruba':
                        '10181'}
CENTRAL_APMANAGER = ['mist', 'cisco']
ARISTA_USER = 'admin'
ARISTA_PASS = 'admin'
MIST_USER = 'admin'
MIST_PASS = 'admin'
USAGE = """USAGE:\n
  gnmicli.py --mode provision  (Provisions AP using provision-aps container)
  OR
  gnmicli.py --mode configure  (Configures AP according to what you put in configs_lib)
  OR
  gnmicli.py --mode monitor  (Issues GetRequests and stores return in TSDB)

  Note, add --dry_run to simply dump & writes JSON used in gNMI SetRequests
  """
