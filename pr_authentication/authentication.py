import json
import requests
import platform
import subprocess
from requests.structures import CaseInsensitiveDict
from jsonpath_ng import jsonpath, parse
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential

###############################################################################
#
# Author:David Edwards
# Ver: 1.0
#
# Description:Call the MS graph API to get machines registered with intune
#
#
###############################################################################

###############################################################################
#Get an Token MS Key - input Client ID of the Service and Secret, returns and oauth token.
###############################################################################
def get_microsoft_token(client_id, client_secret):
 try:
     
  microsoft_auth_url = 'https://login.microsoftonline.com/64b61d8a-7228-432e-8366-af4e7fc1c13e/oauth2/v2.0/token'
 
  headers = CaseInsensitiveDict()
  headers["content-type"] = "application/x-www-form-urlencoded"

  request_body = "grant_type=client_credentials&client_id=" + client_id + "&scope=https%3A%2F%2Fgraph.microsoft.com%2F.default&client_secret=" + client_secret
  token_request  = requests.post(url=microsoft_auth_url, headers=headers,data=request_body)
  auth_response_json = json.loads(token_request.text)

  jsonpath_expression = parse('$..access_token')

  for match in jsonpath_expression.find(auth_response_json):
      return match.value
    
 except Exception as e: 
    print(repr(e))

#Get# get the valut key from Azure Key Vault (VUri = Vault URL,secret_name is the secret to be pulled from the vault tenant_id is the principle tenant_id,
    # client_id is the principle client_id, client_secret is the client secret
  
def get_microsoft_vault_secret(KVUri,secret_name, tenant_id, client_id, client_secret):

 credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
 secretclient = SecretClient(vault_url= KVUri, credential=credential)
    
 token = secretclient.get_secret(secret_name).value
 return token
 






    
