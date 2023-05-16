@ECHO OFF

Echo "run as : createstore [key] [value] [storename]"
Echo "e.g. add  secret keyvalues123 keystore.json"

IF [%1] EQU [] echo Key Name Missing
IF [%2] EQU [] echo Key Vaue Missing
IF [%3] EQU [] echo Store Name Value Missing

set NAME=%1
set VALUE=%2
set STORE_NAME=%3

 
python -c "from prkeystore import *; key_store = prkeystore(); key_store.add_key_pair("""%NAME%""", """%VALUE%""", """%STORE_NAME%""" )"

echo updated keystore %STORE_NAME%
