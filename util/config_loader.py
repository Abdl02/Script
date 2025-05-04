from config.token_generator import get_keycloak_token  
from config.env import Env

def generate_token(env: Env) -> str:
    if not env:
        raise ValueError(f"Environment '{env}' not found.")
    
    token = get_keycloak_token(env)
    if not token:
        raise ValueError("Failed to retrieve token.")
    return token