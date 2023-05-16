import platform
import subprocess
import hashlib 
import json
import os
from dotenv import load_dotenv
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

###############################################################################
#
# Author:David Edwards
# Ver: 1.0
#
# Description:Basic Key Store that links the Machine to a local encrypted key Value pair store. 
#
# key_store = PRKeyStore()
# key_store.create_key_store("secret", "test", "keyfile" )
# key_store.add_key_pair("secret2", "test2", "keyfile")
#
# print(key_store.read_key_value("secret", "keyfile"))
# print(key_store.read_key_value("secret2", "keyfile"))

###############################################################################

class prkeystore:


 SALT =  "q?3.fxphZvST~~3S3vA7DPW+~R}>T'W#6V'CvH#V({jzYzM8+38FyvWT5hWz476M6;cr>t7ZD(2$<,TBJAHM5Md;\f!R`&s'}M),tZcW\^<um34U[gWh<^^L&hUuQM^{"
 HASH_TYPE = 'sha256'
 ROUNDS = 100000

 def __init__(self, *args):
    #check is a salt has been loaded if not load the default .env
    if os.getenv('ENCRYPTION_SALT') is None:
        load_dotenv()

    #check is a salt has been passed
    if len(args) > 0:
        print("here")
        self.SALT = args[0]

    #is salt is avaialble set the value else default will be used
    elif (os.getenv('ENCRYPTION_SALT') is not None):
     self.SALT = os.getenv('ENCRYPTION_SALT')

 ###############################################################################
 # Get an Token MS Key - input Client ID of the Service and Secret, returns and oauth token.
 # Salt can be set if needed, the default is pbkdf2 with SHA 256
 ###############################################################################
 def generate_key(self,salt):

  if platform.system() == 'Windows':
   current_machine_id = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()
  
  if platform.system() == 'Linux':
    current_machine_id = None
     
  if ( current_machine_id is None):
   raise Exception("Sorry, current_machine_id is None")

  if (salt is not None):
   SALT = salt
     
  key = hashlib.pbkdf2_hmac(
    self.HASH_TYPE, # The hash digest algorithm for HMAC
    current_machine_id.encode('utf-8'), # Convert the password to bytes
    self.SALT.encode('utf-8'), # Provide the salt
    100000 # It is recommended to use at least 100,000 iterations of SHA-256
  )

  return key

###############################################################################
# read in the Keystore file for processing 
###############################################################################
 def __read_in_keystore(self, keystore_name_path):
  try:

   file_in = open(keystore_name_path,'rb')

   nonce, tag, ciphertext = [ file_in.read(x) for x in (16, 16, -1) ]
   file_in.close()
   
   return nonce, tag, ciphertext

  except IOError:
    print("Key store does not exist")
    
 def add_key_pair(self, name, value, keystore_name_path):
  try:

   store_data = self.__read_in_keystore(keystore_name_path)
  
   #decrypt the data
   jason_data = json.loads(self.decrypt_aes(store_data[2], store_data[1], store_data[0]))

   # add new keypair
   new_keypair = {name:value}
   jason_data.update(new_keypair)

   # Encrypt the new data 
   encryption_data = self.encrypt_aes(json.dumps(jason_data))
  
   file_out = open(keystore_name_path, "wb")
   [ file_out.write(x) for x in (encryption_data[2], encryption_data[1], encryption_data[0]) ]
   file_out.close()

  except IOError:
    print("Key store does not exist,  Create the Store First")

 
 def encrypt_aes(self, value):

   # The encrypt_and_digest method accepts our data and returns a tuple with the ciphertext
   # and the message authentication code (MAC),
   # sometimes known as a tag, which confirms the authenticity and authority of the data.
  
   cipher = AES.new(self.generate_key(None), AES.MODE_EAX)
   ciphertext, tag = cipher.encrypt_and_digest(bytes(value,'utf-8'))
  
   return ciphertext, tag, cipher.nonce

 def decrypt_aes(self, ciphertext, tag, nonce):
 
   cipher = AES.new(self.generate_key(None), AES.MODE_EAX, nonce)
   data = cipher.decrypt_and_verify(ciphertext, tag) 

   return data.decode('UTF-8')
    
 def create_key_store(self, name, value, keystore_name_path):
  try:
   #encrypt the key  
   details = {name: value}
   encryption_data = self.encrypt_aes(json.dumps(details))
  
   file_out = open(keystore_name_path, "wb")
   [ file_out.write(x) for x in (encryption_data[2], encryption_data[1], encryption_data[0]) ]
   file_out.close()
  except IOError:
     print("Error creating keystore")
    

 def read_key_value(self, name, keystore_name_path):
   
    store_data = self.__read_in_keystore(keystore_name_path)
  
    #decrypt the data
    jason_data = json.loads(self.decrypt_aes(store_data[2], store_data[1], store_data[0]))


    for key, value in jason_data.items():
        
     if key == name:
      return value
  
    return None    
