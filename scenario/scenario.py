import sys
import os

from config.config import Config
from scenario.api_request import APIRequest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import os
from validation.endpoint_validations import ValidatorFactory, manipulate_and_create_random_data
import re

load_dotenv(dotenv_path=".env")



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

    def execute(self, initial_context: Dict[str, Any] = None) -> list[Any]:
        """Executes the requests in the scenario, handling dependencies based on 'save_as'."""
        context = initial_context if initial_context else {}

        # A Map to store the request with its response
        request_response_map = {}
        runResults = []

        envUrl = Config.selected_env.envUrl

        for request in self.requests:
            if request.url.startswith("/"):
                request.url = envUrl + request.url
            elif not request.url.startswith("http") or not request.url.startswith("https"):
                request.url = envUrl + "/" + request.url


            try:
                # If size of request_response_map is greater than 0, it means we have already executed some requests
                if request_response_map:
                    # Process request body template variables
                    if request.body:
                        self._process_template_values_recursive(request.body, request_response_map)

                    # Process URL template variables
                    if request.url:
                        self._process_template_url(request, request_response_map)

                if request.method in ["POST", "PUT", "PATCH"]:
                    request.body = manipulate_and_create_random_data(request.body, request.url)

                runResults.append(request.execute(context))
                # Store the response content in the request_response_map
                request_response_map[request.name] = request.response.content
            except Exception as e:
                print(f"  {request.name}: Error during execution - {e}")
                # Optionally stop the scenario execution here
            print("-" * 20)
        return runResults

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


def get_all_field_paths(body: Dict[str, Any], prefix: str = "") -> List[str]:
    """Get all field paths in a nested dictionary."""
    paths = []

    if not isinstance(body, dict):
        return paths

    for key, value in body.items():
        current_path = f"{prefix}.{key}" if prefix else key
        paths.append(current_path)

        if isinstance(value, dict):
            paths.extend(get_all_field_paths(value, current_path))
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            paths.extend(get_all_field_paths(value[0], f"{current_path}[0]"))

    return paths


def get_value_from_path(data, path):
    """Helper function to get a value from a nested dictionary using a path string"""
    if not path:
        return None

    parts = path.split('.')
    current = data

    for part in parts:
        if '[' in part and ']' in part:
            name = part[:part.index('[')]
            index = int(part[part.index('[') + 1:part.index(']')])

            if name not in current:
                return None

            current = current[name]
            if not isinstance(current, list) or index >= len(current):
                return None

            current = current[index]
        else:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

    return current