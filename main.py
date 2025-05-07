from config.config import Config
from runtime.flow_runner import run, save_scenario, list_scenarios
from scenario.scenario import *

def main():
    user_input = input("Enter the environment (e.g., localDev, production): ")

    # 1. Run a scenario
    # 2. Create and save a scenario
    # 3. List all scenarios
    # 4. Exit
    while True:
        print("1. Run a scenario")
        print("2. Create and save a scenario")
        print("3. List all scenarios")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1' or choice == '2':
            scenario_name = input("Enter the scenario name: ")
            if choice == '2':
                scenario = create_new_scenario()
                save_scenario(scenario)
            else:
                run(scenario_name, user_input)
        elif choice == '3':
            scenarios = list_scenarios()
            print("Available scenarios:", scenarios)
        elif choice == '4':
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()