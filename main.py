from config.config import Config
from runtime.flow_runner import run, save_scenario
from scenrio.scenario import *

def main():
    user_input = input("Enter the environment (e.g., localDev, production): ")
    Config.set_selected_env(user_input)

    # Create or execute a scenario
    scenario_name = input("Enter the scenario name (or 'new' to create a new one): ")
    if scenario_name.lower() == 'new':
        # Create a new scenario
        scenario = create_new_scenario()
        if save_scenario(scenario):
            print(f"Scenario '{scenario.name}' saved successfully.")
        else:
            print("Failed to save the scenario.")
    else:
        # Execute an existing scenario
        if run(scenario_name):
            print(f"Scenario '{scenario_name}' executed successfully.")
        else:
            print("Failed to execute the scenario.")

if __name__ == "__main__":
    main()