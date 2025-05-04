from config.token_generator import get_keycloak_token  
from config.env import envs

def generate_token(env: str) -> str:
    env = envs.get(env)
    if not env:
        raise ValueError(f"Environment '{env}' not found.")
    
    token = get_keycloak_token(env)
    if not token:
        raise ValueError("Failed to retrieve token.")
    return token