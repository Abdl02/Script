

from scenrio.scenario import *
from util.yaml_utils import *
import os


def run(scenarioName: str) -> bool:
    """
    Run the specified scenario.
    """
    try:
        # Get the full path of the scenario file
        path = get_scenario_path(scenarioName)

        # Check if the YAML file exists
        is_yaml_exists(path)

        # Load the scenario YAML file
        scenario = yaml_file_to_object(path, TestScenario)

        # Execute the scenario
        scenario.execute()

        return True  # Indicate success
    except Exception as e:
        print(f"Error while running scenario: {e}")
        return False  # Indicate failure

def save_scenario(scenario: TestScenario) -> bool:
    """
    Save the scenario to a YAML file.
    """
    try:
        # Get the full path of the scenario file
        path = get_scenario_path(scenario.name)

        # Save the scenario to the YAML file
        object_to_yaml_file(scenario, path)

        return True  # Indicate success
    except Exception as e:
        print(f"Error while saving scenario: {e}")
        return False  # Indicate failure

def list_scenarios() -> list:
    """
    List all scenarios in the scenario directory.
    """
    scenario_save_dir = os.getenv("SCENARIO_SAVE_DIR", "./")
    os.makedirs(scenario_save_dir, exist_ok=True)

    # List all YAML files in the scenario directory
    scenario_files = [f for f in os.listdir(scenario_save_dir) if f.endswith('.yaml')]

    # Return the list of scenario names without extensions
    return [os.path.splitext(f)[0] for f in scenario_files]

def get_scenario_path(scenarioName: str) -> str:
    """
    Get the full path of the scenario file.
    """
    scenario_save_dir = os.getenv("SCENARIO_SAVE_DIR", "./")
    os.makedirs(scenario_save_dir, exist_ok=True)
    return os.path.join(scenario_save_dir, handleExtension(scenarioName))


def handleExtension(scenarioName: str) -> str:
    """
    Handle the extension of the scenario name.
    """
    if not scenarioName.endswith(".yaml"):
        scenarioName += ".yaml"
    return scenarioName