import sys
import re
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
r = requests.get(url + '/api/show/volumes', headers=headers, verify=False)

response = json.loads(r.content)

channels = []

for volume in response['volumes']:
    total_space = float(volume['size'][:-2])
    allocated_space = float(re.search(r'\d+\.\d+', volume['allocated-size']).group())
    free_space = total_space - allocated_space
    used_space = total_space - free_space
    percentage_free = (free_space / total_space) * 100
    channel = {
        'channel': volume['volume-name'] + ' - capacity',
        'value': percentage_free,
        'unit': 'Percent',
        'float': 1
    }
    channels.append(channel)
    
# Construct the JSON payload
payload = {"prtg": {"result": channels}}

# Output the JSON payload
print(json.dumps(payload))
