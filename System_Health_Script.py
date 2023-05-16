import sys
import json
import hashlib
import requests


# Suppress insecure connection warning for certificate verification.
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#Will return the value of the key pair 
from pr_authentication.prkeystore import prkeystore
keystore = prkeystore()

#load prtg data, used to gather device name dynamically in this script
data = json.loads(sys.argv[1])

USE_BASIC_AUTH = 1
url = "https://" + data["host"]
username = keystore.read_key_value ("username", "C:\\Program Files (x86)\\PRTG Network Monitor\\Custom Sensors\\python\\pr_authentication\\keystore.json")  #"svc-obs-python"
#print(username)
password = keystore.read_key_value ("password", "C:\\Program Files (x86)\\PRTG Network Monitor\\Custom Sensors\\python\\pr_authentication\\keystore.json")
#print(password)
#output_file = "C:\\pyrc\\test.txt"

if USE_BASIC_AUTH:
    # HTTP basic authentication
    headers = {'datatype': 'json'}
    r = requests.get(url + '/api/login', auth=(username, password), headers=headers, verify=False)
else:
    # SHA-256 authentication
    auth_bytes = bytes(username + '_' + password, 'utf-8')
    auth_string = hashlib.sha256(auth_bytes).hexdigest()
    headers = {'datatype': 'json'}
    r = requests.get(url + '/api/login/' + auth_string, headers=headers, verify=False)

# Extract session key from response
response = json.loads(r.content.decode('utf-8'))
sessionKey = response['status'][0]['response']

# Obtain the health of the system
headers = {'sessionKey': sessionKey, 'datatype': 'json'}
r = requests.get(url + '/api/show/system', headers=headers, verify=False)

response = json.loads(r.content)
#print(response)
if response['system'][0]['health'] == 'OK':
    status = 0
    result = {"prtg": {"result": [{"channel": "System Health", "value": status}]}}
else:
    status = 1
    result = {"prtg": {"result": [{"channel": "System Health", "value": status}], "text": response['system'][0]['health']}}

#with open(output_file, "w") as f:
#    f.write(json.dumps(result))

print(json.dumps(result))
