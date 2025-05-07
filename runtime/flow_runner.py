import traceback

from config.config import Config
from scenrio.scenario import *
from util.yaml_utils import *
import os


def run(scenarioName: str, environment: str):
    """
    Run the specified scenario.
    """
    # Check if the scenario name is valid
    if not scenarioName:
        raise ValueError("Scenario name cannot be empty.")
    # Check if the environment is valid
    if not environment:
        raise ValueError("Environment cannot be empty.")

    Config.set_selected_env(environment)

    # Get the full path of the scenario file
    path = get_scenario_path(scenarioName)

    # Check if the YAML file exists
    isExists = is_yaml_exists(path)
    if not isExists:
        raise FileNotFoundError(f"Scenario '{scenarioName}' does not exist.")

    # Load the scenario YAML file
    scenario = yaml_file_to_object(path, TestScenario)

    # Execute the scenario
    results = scenario.execute()
    numberOfFailedRequests = 0
    for result in results:
        # The results are dictionaries, not objects, so use dictionary access
        if result["status"]["text"] == "FAILED":
            numberOfFailedRequests += 1

    final_results = {
        "requests": results,
        "numberOfRequests": len(results),
        "status": "success" if numberOfFailedRequests == 0 else "failed",
    }

    return final_results

def save_scenario(scenario: TestScenario) -> bool:
    """
    Save the scenario to a YAML file.
    """
    try:
        # Get the full path of the scenario file
        path = get_scenario_path(scenario.name)

        # Check if a scenario with same name already exists
        if is_yaml_exists(path):
            raise FileExistsError(f"Scenario '{scenario.name}' already exists. Please choose a different name.")

        for req in (scenario.requests or []):
            # replace space with underscore
            req.name = req.name.replace(" ", "_")
            req.save_as = req.name

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