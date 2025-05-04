import requests
import json
from typing import Dict, Any
from config.envModel import Env, DEFAULTS

def get_keycloak_token(env :Env) -> str:
    url = f"{env.urlKeycloak}/realms/{env.realm}/protocol/openid-connect/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": env.clientId,
        "client_secret": env.clientSecret,
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get token: {response.status_code} {response.text}")

    return response.json().get("access_token", "")