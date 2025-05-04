import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from typing import List, Dict, Any
from scenrio.api_request import APIRequest
from util.yaml_mapper.yaml_utils import object_to_yaml_file
import datetime
from dotenv import load_dotenv
import os
from validation.endpoint_validations import ValidatorFactory
from validation.random_data_factory import RandomDataFactory

load_dotenv(dotenv_path=".env")

LOCALDEV_BASE_URL = os.getenv("LOCALDEV_ENV_URL", "http://localhost:8099")


class TestScenario:
    def __init__(self, name: str, id: str, description: str, version: str, created_at: str, updated_at: str,
                 requests: List[Dict[str, Any]]):
        self.name = name
        self.id = id
        self.description = description
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at
        self.requests: List[APIRequest] = self._parse_requests(requests)

    def _parse_requests(self, requests_data: List[Dict[str, Any]]) -> List[APIRequest]:
        requests = []
        for req_data in requests_data:
            requests.append(APIRequest(**req_data))
        return requests

    def execute(self, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Executes the requests in the scenario, handling dependencies based on 'save_as'."""
        context = initial_context if initial_context else {}
        for request in self.requests:
            print(f"Executing: {request.name}")
            try:
                request.execute(context)
                if request.save_as and request.saved_data:
                    context[request.save_as] = request.saved_data
                request.validate_assertions()
                print(f"  {request.name}: Assertions passed")
            except AssertionError as e:
                print(f"  {request.name}: Assertion failed - {e}")
                # Optionally stop the scenario execution here
            except Exception as e:
                print(f"  {request.name}: Error during execution - {e}")
                # Optionally stop the scenario execution here
            print("-" * 20)
        return context

    def to_dict(self) -> Dict[str, Any]:
        """Converts the scenario object to a dictionary for saving."""
        return {
            "name": self.name,
            "id": self.id,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "requests": [
                {
                    "name": req.name,
                    "method": req.method,
                    "url": req.url,
                    "headers": req.headers,
                    "body": req.body,
                    "save_as": req.save_as,
                    "assertions": req.assertions,
                }
                for req in self.requests
            ],
        }


def create_new_scenario():
    """Prompts the user to create a new test scenario."""
    scenario_name = input("Enter scenario name: ")
    scenario_id = input("Enter scenario ID: ")
    scenario_description = input("Enter scenario description: ")
    scenario_version = input("Enter scenario version: ")
    now = datetime.datetime.utcnow().isoformat() + "Z"
    requests = []
    num_endpoints = int(input("Enter the number of endpoints in this scenario: "))

    for i in range(num_endpoints):
        print(f"\n--- Endpoint {i + 1} ---")
        request_name = input("Enter request name: ")
        method = input("Enter HTTP method (GET/POST/PUT/DELETE/...): ").upper()
        path = input("Enter endpoint path (e.g., 'api-specs'): ").strip().lstrip("/")
        url = f"{LOCALDEV_BASE_URL}/{path}"

        # Get the appropriate validator based on the endpoint path
        endpoint_type = path.split("/")[0]  # Assuming the first part of the path indicates the endpoint type
        validator = ValidatorFactory.get_validator(endpoint_type)

        # Generate valid request body based on the endpoint type
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            if validator:
                if hasattr(validator, 'get_valid_body'):
                    body = validator.get_valid_body()
                else:
                    print(f"Warning: No 'get_valid_body' method found for endpoint type '{endpoint_type}'.")
                    body_input = input("Enter the request body manually (as JSON or leave empty): ").strip()
                    try:
                        if body_input:
                            body = json.loads(body_input)
                    except json.JSONDecodeError:
                        print("Error: Invalid JSON format entered for the request body.")
            else:
                print(f"No validator found for endpoint type '{endpoint_type}'. Skipping automatic request body generation.")
                body_input = input("Enter the request body manually (as JSON or leave empty): ").strip()
                try:
                    if body_input:
                        body = json.loads(body_input)
                except json.JSONDecodeError:
                    print("Error: Invalid JSON format entered for the request body.")

        save_as = input("Enter a name to save the response data (or leave empty): ")
        assertions = []
        num_assertions = int(input("Enter the number of assertions for this endpoint: "))
        for j in range(num_assertions):
            print(f"  --- Assertion {j + 1} ---")
            assertion_type = input("  Enter assertion type (status_code/json_path/response_body_contains): ")
            assertion_value = input("  Enter expected value for the assertion: ")
            assertion_path = input("  Enter JSON path (if applicable, else leave empty): ")
            assertion_data = {"type": assertion_type, "value": assertion_value}
            if assertion_path:
                assertion_data["path"] = assertion_path
            assertions.append(assertion_data)

        requests.append({
            "name": request_name,
            "method": method,
            "url": url,
            "headers": {},  # You can add headers if needed
            "body": body,
            "save_as": save_as if save_as else None,
            "assertions": assertions,
        })

    new_scenario = TestScenario(
        name=scenario_name,
        id=scenario_id,
        description=scenario_description,
        version=scenario_version,
        created_at=now,
        updated_at=now,
        requests=requests,
    )
    return new_scenario


def save_scenario_to_json(scenario: TestScenario, filename: str = "scenario.json"):
    """Saves a TestScenario object to a JSON file."""
    with open(filename, "w") as f:
        json.dump(scenario.to_dict(), f, indent=2)
    print(f"Scenario '{scenario.name}' saved to '{filename}'")


def convert_scenario_json_to_yaml(json_path: str = "scenario.json", yaml_path: str = "scenario.yaml"):
    """Reads scenario.json and writes it as scenario.yaml"""
    with open(json_path, "r") as f:
        data = json.load(f)
        scenario = TestScenario(**data)
        object_to_yaml_file(scenario, yaml_path)
        print(f"Scenario copied from '{json_path}' to '{yaml_path}'")


if __name__ == "__main__":
    new_scenario = create_new_scenario()
    save_scenario_to_json(new_scenario)
    convert_scenario_json_to_yaml()
    print("\nScenario saved to scenario.json")