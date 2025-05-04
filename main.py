from util.config_loader import generate_token
from runtime.template_processor import *

if __name__ == "__main__":
    current_env_name = "localDev" 
    token = generate_token(current_env_name)

    print(f"SCENARIO_SAVE_DIR: {get_scenario_save_dir()}")