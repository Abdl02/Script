import requests
import json
import re
from typing import Dict, Any, Optional
from util.token_util import *
from config.config import Config


class APIRequest:
    def __init__(self, name: str, method: str, url: str, headers: Optional[Dict[str, str]] = None,
                 body: Optional[Any] = None):
        self.name = name
        self.method = method.upper()
        self.url = url
        self.headers = headers if headers is not None else {}
        self.body = body
        self.response = None
        self.saved_data: Dict[str, Any] = {}

    def execute(self, context: Dict[str, Any]):
        """Executes the API request using the provided context for templating."""
        # Create a dictionary to collect execution details
        execution_details = {
            "name": self.name,
            "status": "unknown",
            "details": {}
        }

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
            execution_details["details"]["response"]["body"] = self.response.text[
                                                               :500] if self.response.text else ""

        formatted_output = self.format_request_response_details(
            execution_details, templated_url, templated_headers, templated_body
        )
        return formatted_output


    def _template(self, value: str, context: Dict[str, Any]) -> str:
        """Enhanced templating for URLs and headers using the context, supporting both {{key}} and ${key} syntax."""
        if not value or not isinstance(value, str):
            return value

        # Debug: Print what we're trying to resolve
        print(f"DEBUG: Original value: {value}")
        print(f"DEBUG: Context: {json.dumps(context, indent=2)}")

        # Handle ${key.subkey} references
        def replace_dollar_reference(match):
            reference = match.group(1)
            print(f"DEBUG: Trying to resolve reference: {reference}")
            try:
                # Split reference into parts (e.g., "create_api_my.id" -> ["create_api_my", "id"])
                parts = reference.split('.')
                val = context

                # Navigate through the context
                for part in parts:
                    print(f"DEBUG: Looking for part '{part}' in: {type(val)}")
                    if isinstance(val, dict) and part in val:
                        val = val[part]
                        print(f"DEBUG: Found value: {val}")
                    else:
                        # Reference not found, return the original reference
                        print(f"DEBUG: Part '{part}' not found!")
                        return match.group(0)

                # Return the resolved value
                print(f"DEBUG: Successfully resolved to: {str(val)}")
                return str(val)
            except Exception as e:
                print(f"Error resolving reference ${reference}: {e}")
                return match.group(0)

        # Handle ${...} pattern
        value = re.sub(r'\$\{([^}]+)\}', replace_dollar_reference, value)

        # Handle {{...}} pattern (backward compatibility)
        for key, val in context.items():
            placeholder = f"{{{{{key}}}}}"
            value = value.replace(placeholder, str(val))

        print(f"DEBUG: Final resolved value: {value}")
        return value

    def _template_body(self, body: Optional[Any], context: Dict[str, Any]) -> Optional[Any]:
        """Templates the request body. Currently only handles JSON-like structures."""
        if isinstance(body, str):
            try:
                body_dict = json.loads(body)
                return self._template_recursive(body_dict, context)
            except json.JSONDecodeError:
                return self._template(body, context)  # Basic string templating if not JSON
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

    def __repr__(self):
        return f"<APIRequest(name='{self.name}', method='{self.method}', url='{self.url}')>"

    def format_request_response_details(self, execution_details, templated_url, templated_headers, templated_body):
        """Format request and response details into structured JSON output and return as RunResult"""
        # Set status in execution details
        execution_details["status"] = "SUCCESS" if self.response.ok else "FAILED"

        # Create structured JSON output
        formatted_json = {
            "name": self.name,
            "status": {
                "code": self.response.status_code,
                "text": "SUCCESS" if self.response.ok else "FAILED"
            },
            "request": {
                "url": templated_url,
                "method": self.method,
                "headers": templated_headers,
                "body": templated_body
            },
            "response": {
                "status": self.response.status_code,
                "body": execution_details['details']['response']['body'],
                "headers": execution_details['details']['response'].get('headers', {})
            }
        }

        status = "SUCCESS" if self.response.ok else "FAILED"
        if self.response.ok:
            formatted_json["status"]["text"] = "SUCCESS"
        else:
            formatted_json["status"]["text"] = "FAILED"
        return formatted_json