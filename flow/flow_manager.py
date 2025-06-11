from scenario.scenario import TestScenario
from util.yaml_utils import object_to_yaml_file, yaml_file_to_object, is_yaml_exists
from util.config_loader import generate_token
from config.envModel import envs, Env


def run_scenario(scenario: TestScenario, env: str):
    """
    Run a scenario with the given environment.

    :param scenario: The scenario to run.
    :param env: The environment to use.
    """
    # Load the scenario
    scenario.load()

    # Generate the token for the specified environment
    token = generate_token(env)

    # Execute the scenario with the generated token
    scenario.execute(token)
