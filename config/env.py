import os
from typing import Dict
from dotenv import load_dotenv

class Env:
    def __init__(self, clientId: str, clientSecret: str, urlKeycloak: str, realm: str, envUrl: str):
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.urlKeycloak = urlKeycloak
        self.realm = realm
        self.envUrl = envUrl

    def __str__(self):
        return f"Env(clientId={self.clientId}, clientSecret={self.clientSecret}, urlKeycloak={self.urlKeycloak}, realm={self.realm}, envUrl={self.envUrl})"


# Load environment variables from the .env file
load_dotenv()

# Default values for environments using environment variables
DEFAULTS = {
    "dev": {
        "clientId": os.getenv("DEV_CLIENT_ID", "defaultClientId"),
        "clientSecret": os.getenv("DEV_CLIENT_SECRET", "defaultClientSecret"),
        "urlKeycloak": os.getenv("DEV_URL_KEYCLOAK", "https://default-keycloak.example.com"),
        "realm": os.getenv("DEV_REALM", "defaultRealm"),
        "envUrl": os.getenv("DEV_ENV_URL", "https://default.example.com")
    },
    "localDev": {
        "clientId": os.getenv("LOCALDEV_CLIENT_ID", "3DnNzNhSw5p7qhtbg1WRqAnozYpO5hgy+PhXAMKIg1Y="),
        "clientSecret": os.getenv("LOCALDEV_CLIENT_SECRET", "bQrqlsv8ESFU9YwtqL3CCyiFIAdS2vcl"),
        "urlKeycloak": os.getenv("LOCALDEV_URL_KEYCLOAK", "http://localhost:8080"),
        "realm": os.getenv("LOCALDEV_REALM", "dgate"),
        "envUrl": os.getenv("LOCALDEV_ENV_URL", "http://localhost:8099")
    },
    "test": {
        "clientId": os.getenv("TEST_CLIENT_ID", "defaultTestClientId"),
        "clientSecret": os.getenv("TEST_CLIENT_SECRET", "defaultTestClientSecret"),
        "urlKeycloak": os.getenv("TEST_URL_KEYCLOAK", "https://default-test-keycloak.example.com"),
        "realm": os.getenv("TEST_REALM", "defaultTestRealm"),
        "envUrl": os.getenv("TEST_ENV_URL", "https://default-test.example.com")
    }
}

def create_env(name: str) -> Env:
    config = DEFAULTS.get(name)
    if not config:
        raise ValueError(f"Environment '{name}' not found in DEFAULTS.")
    return Env(**config)

# Create environments dynamically
envs: Dict[str, Env] = {name: create_env(name) for name in DEFAULTS.keys()}

# Example usage
if __name__ == "__main__":
    for name, env in envs.items():
        print(f"{name}: {env}")