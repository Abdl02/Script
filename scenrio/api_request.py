import requests
import json
from typing import Dict, Any, Optional
from util.config_loader import *
from config.config import Config

class APIRequest:
    def __init__(self, name: str, method: str, url: str, headers: Optional[Dict[str, str]] = None, body: Optional[Any] = None, save_as: Optional[str] = None, assertions: Optional[list[Dict[str, Any]]] = None):
        self.name = name
        self.method = method.upper()
        self.url = url
        self.headers = headers if headers is not None else {}
        self.body = body
        self.save_as = save_as
        self.assertions = assertions if assertions is not None else []
        self.response = None
        self.saved_data: Dict[str, Any] = {}

    def execute(self, context: Dict[str, Any]) -> None:
        """Executes the API request using the provided context for templating."""
        # Create a dictionary to collect execution details
        execution_details = {
            "name": self.name,
            "status": "unknown",
            "details": {}
        }

        try:
            token = generate_token(Config.selected_env)
            if token:
                self.headers["Authorization"] = f"Bearer {token}"

            templated_url = self._template(self.url, context)
            templated_headers = {k: self._template(v, context) for k, v in self.headers.items()}
            templated_body = self._template_body(self.body, context)

            # Record request details
            execution_details["details"]["request"] = {
                "url": templated_url,
                "method": self.method,
                "headers": templated_headers,
                "body": templated_body
            }

            if self.method == "GET":
                self.response = requests.get(templated_url, headers=templated_headers)
            elif self.method == "POST":
                self.response = requests.post(templated_url, headers=templated_headers, json=templated_body)
            elif self.method == "PUT":
                self.response = requests.put(templated_url, headers=templated_headers, json=templated_body)
            elif self.method == "DELETE":
                self.response = requests.delete(templated_url, headers=templated_headers)
            # Add other HTTP methods as needed
            else:
                raise ValueError(f"Unsupported HTTP method: {self.method}")

            # Record response details
            execution_details["details"]["response"] = {
                "status_code": self.response.status_code,
                "headers": dict(self.response.headers)
            }

            # Try to parse response as JSON
            try:
                response_json = self.response.json()
                execution_details["details"]["response"]["body"] = response_json
            except json.JSONDecodeError:
                execution_details["details"]["response"]["body"] = self.response.text[:500] if self.response.text else ""

            formatted_output = self.format_request_response_details(
                execution_details, templated_url, templated_headers, templated_body
            )
            print(formatted_output)

        except requests.exceptions.RequestException as e:
            execution_details["status"] = "failed"
            execution_details["details"]["error"] = str(e)
            print(f"Error executing request '{self.name}': {e}")
            print(f"Request details: {json.dumps(execution_details, indent=4)}")
            raise e

    def _template(self, value: str, context: Dict[str, Any]) -> str:
        """Simple templating for URLs and headers using the context."""
        for key, val in context.items():
            placeholder = f"{{{{{key}}}}}"
            value = value.replace(placeholder, str(val))
        return value

    def _template_body(self, body: Optional[Any], context: Dict[str, Any]) -> Optional[Any]:
        """Templates the request body. Currently only handles JSON-like structures."""
        if isinstance(body, str):
            try:
                body_dict = json.loads(body)
                return self._template_recursive(body_dict, context)
            except json.JSONDecodeError:
                return self._template(body, context) # Basic string templating if not JSON
        elif isinstance(body, dict):
            return self._template_recursive(body, context)
        elif isinstance(body, list):
            return [self._template_recursive(item, context) for item in body]
        return body

    def _template_recursive(self, data: Any, context: Dict[str, Any]) -> Any:
        """Recursively templates values within dictionaries and lists."""
        if isinstance(data, str):
            return self._template(data, context)
        elif isinstance(data, dict):
            return {k: self._template_recursive(v, context) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._template_recursive(item, context) for item in data]
        return data

    def validate_assertions(self) -> bool:
        """Validates the assertions against the response."""
        if not self.response:
            raise Exception(f"Request '{self.name}' has not been executed yet.")

        for assertion in self.assertions:
            assertion_type = assertion.get("type")
            expected_value = assertion.get("value")

            if assertion_type == "status_code":
                if self.response.status_code != int(expected_value):
                    raise AssertionError(f"Assertion failed for '{self.name}': Expected status code {expected_value}, got {self.response.status_code}")
            elif assertion_type == "json_path":
                path = assertion.get("path")
                try:
                    from jsonpath_ng.ext import parse
                    jsonpath_expression = parse(path)
                    match = jsonpath_expression.find(self.response.json())
                    if not match or str(match[0].value) != expected_value:
                        raise AssertionError(f"Assertion failed for '{self.name}': JSON path '{path}' expected value '{expected_value}', got '{match[0].value if match else None}'")
                except ImportError:
                    print("Warning: 'jsonpath-ng' library not installed. JSON path assertions will be skipped.")
                except json.JSONDecodeError:
                    raise AssertionError(f"Assertion failed for '{self.name}': Cannot decode response as JSON for JSON path assertion.")
            elif assertion_type == "response_body_contains":
                if expected_value not in self.response.text:
                    raise AssertionError(f"Assertion failed for '{self.name}': Response body does not contain '{expected_value}'")
            # Add other assertion types as needed
            else:
                print(f"Warning: Unknown assertion type '{assertion_type}' for request '{self.name}'.")
        return True

    def __repr__(self):
        return f"<APIRequest(name='{self.name}', method='{self.method}', url='{self.url}')>"

    def format_request_response_details(self, execution_details, templated_url, templated_headers, templated_body):
        """Format request and response details into a structured output"""
        status_emoji = "✅" if self.response.ok else "❌"
        status_text = "Success" if self.response.ok else "Failed"
        execution_details["status"] = "success" if self.response.ok else "failed"

        # Create formatted sections
        header = f"\n{'=' * 50}\n  {self.name} - {status_emoji} {status_text} (Status: {self.response.status_code})\n{'=' * 50}"

        request_section = [
            "\n📤 REQUEST:",
            f"  URL: {templated_url}",
            f"  Method: {self.method}"
        ]

        if templated_headers:
            request_section.append(f"  Headers:\n{json.dumps(templated_headers, indent=4).replace('^', '  ')}")

        if templated_body:
            request_section.append(f"  Body:\n{json.dumps(templated_body, indent=4).replace('^', '  ')}")

        response_section = [
            "\n📥 RESPONSE:",
            f"  Status: {self.response.status_code}"
        ]

        response_body = execution_details['details']['response']['body']
        if response_body:
            if isinstance(response_body, dict) or isinstance(response_body, list):
                response_section.append(f"  Body:\n{json.dumps(response_body, indent=4).replace('^', '  ')}")
            else:
                response_section.append(f"  Body: {response_body}")

        # Combine all sections
        output = [
            header,
            "\n".join(request_section),
            "\n".join(response_section),
            f"\n{'=' * 50}\n"
        ]

        return "\n".join(output)
