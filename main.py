from util.config_loader import generate_token

if __name__ == "__main__":
    current_env_name = "localDev" 
    token = generate_token(current_env_name)