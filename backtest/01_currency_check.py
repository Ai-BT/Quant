# %%
import jwt
import requests
import uuid
from config.api_config import access_key, secret_key, server_url

payload = {
    'access_key': access_key,
    'nonce': str(uuid.uuid4()),
}

jwt_token = jwt.encode(payload, secret_key)
authorization = 'Bearer {}'.format(jwt_token)
headers = {
    'Authorization': authorization,
}

res = requests.get(server_url + '/v1/accounts', headers=headers)
data = res.json()

for row in data:
    currency = row.get('currency')
    balance = row.get('balance')
    locked = row.get('locked')

    # print(currency)

    if currency in ("XRP", "SOL", "BTC"):
         print(currency, balance)
