from util.yaml_mapper import *
import os

def get_scenario_save_dir():
    scenario_save_dir = os.getenv("SCENARIO_SAVE_DIR", "./")
    os.makedirs(scenario_save_dir, exist_ok=True)
    return scenario_save_dir