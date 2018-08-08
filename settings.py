import os
from os.path import join, dirname
from dotenv import load_dotenv
 
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
 
# Accessing variables.
status = os.getenv('CLIENT_ID')
secret_key = os.getenv('CLIENT_SECRET')
verification = os.getenv('VERIFICATION')
oauth_token = os.getenv('OAUTH_TOKEN')
 
# Using variables.
print(status)
print(secret_key)
print(verification)
print(oauth_token)