import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from typing import List, Dict, Any
from scenrio.api_request import APIRequest
import datetime
from dotenv import load_dotenv
import os
from validation.endpoint_validations import ValidatorFactory
import re

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

        # A Map to store the request with its response
        request_response_map = {}

        for request in self.requests:

            print(f"Executing: {request.name}")
            try:
                # If size of request_response_map is greater than 0, it means we have already executed some requests
                if request_response_map:
                    # Process request body template variables
                    if request.body:
                        self._process_template_values_recursive(request.body, request_response_map)

                    # Process URL template variables
                    if request.url:
                        self._process_template_url(request, request_response_map)



                request.execute(context)
                # Store the response content in the request_response_map
                request_response_map[request.name] = request.response.content
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

    def _process_template_url(self, request: APIRequest, request_response_map: Dict[str, Any]):
        url_variables = self.extract_variables(request.url)
        for var_name in url_variables:
            path_components = var_name.split(".")
            source_key = path_components[0]

            if source_key in request_response_map:
                source_data = request_response_map[source_key]

                if len(path_components) > 1:
                    # Use path resolution for nested objects
                    resolved_value = self._resolve_nested_path(source_data, path_components[1:])
                    if resolved_value is not None:
                        replacement_value = str(resolved_value)
                        request.url = request.url.replace(f"{{{{{var_name}}}}}", replacement_value)
                    else:
                        print(
                            f"Warning: Path '{'.'.join(path_components[1:])}' not found in '{source_key}'. Skipping URL replacement.")
                else:
                    replacement_value = str(source_data)
                    request.url = request.url.replace(f"{{{{{var_name}}}}}", replacement_value)
            else:
                print(
                    f"Warning: Variable '{source_key}' not found in response map. Skipping URL replacement.")

    def _resolve_nested_path(self, data: Any, path_components: list) -> Any:
        """Resolves a nested path in data structure like 'response.data.id'."""
        # convert data to dict if it's a string, or bytes
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return None
        elif isinstance(data, bytes):
            try:
                data = json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                return None
        current = data
        for component in path_components:
            if isinstance(current, dict) and component in current:
                current = current[component]
            elif isinstance(current, list) and component.isdigit():
                index = int(component)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                return None
        return current

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

    def _process_template_values_recursive(self, data, request_response_map):
        """Process template variables recursively in nested structures."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and "{{" in value and "}}" in value:
                    # Extract variable name from the template string
                    var_name = value.strip("{{").strip("}}")
                    # Parse the path components
                    path_components = var_name.split(".")
                    source_key = path_components[0]

                    if source_key in request_response_map:
                        source_data = request_response_map[source_key]

                        if len(path_components) > 1:
                            # Use path resolution for nested objects
                            resolved_value = self._resolve_nested_path(source_data, path_components[1:])
                            if resolved_value is not None:
                                data[key] = resolved_value
                            else:
                                print(
                                    f"Warning: Path '{'.'.join(path_components[1:])}' not found in '{source_key}'. Skipping replacement.")
                        else:
                            data[key] = source_data
                    else:
                        print(f"Warning: Variable '{source_key}' not found in response map. Skipping replacement.")
                elif isinstance(value, (dict, list)):
                    # Recursively process nested objects/arrays
                    self._process_template_values_recursive(value, request_response_map)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str) and "{{" in item and "}}" in item:
                    # Handle template strings in lists
                    var_name = item.strip("{{").strip("}}")
                    path_components = var_name.split(".")
                    source_key = path_components[0]

                    if source_key in request_response_map:
                        source_data = request_response_map[source_key]
                        if len(path_components) > 1:
                            resolved_value = self._resolve_nested_path(source_data, path_components[1:])
                            if resolved_value is not None:
                                data[i] = resolved_value
                        else:
                            data[i] = source_data
                elif isinstance(item, (dict, list)):
                    # Recursively process nested objects/arrays in lists
                    self._process_template_values_recursive(item, request_response_map)

    # Get all {{}} variables from the url
    def extract_variables(self, string: str) -> list:
        """
        Extract all {{}} variables from a string.
        """
        pattern = r"\{\{(.*?)\}\}"
        matches = re.findall(pattern, string)
        return [match.strip() for match in matches]

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