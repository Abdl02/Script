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
import re
import uuid
import random
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


def handle_path_parameters(path: str, context: Dict[str, Any] = None) -> str:
    """Handle path parameters with the option to reference previous response data."""

    # Check if path contains parameters (marked with {})
    if '{' not in path or '}' not in path:
        return path

    print(f"\nPath contains parameters: {path}")
    print("How would you like to fill these parameters?")
    print("1. Enter values manually")
    print("2. Use values from previous responses")
    print("3. Generate random values")
    choice = input("Enter your choice (1-3): ")

    if choice == "1":
        # Manual entry
        return fill_path_params_manually(path)
    elif choice == "2":
        # Reference from previous responses
        return fill_path_params_from_references(path, context)
    elif choice == "3":
        # Generate random values
        return fill_path_params_randomly(path)
    else:
        print("Invalid choice. Using manual entry.")
        return fill_path_params_manually(path)


def fill_path_params_manually(path: str) -> str:
    """Fill path parameters with manual input."""
    param_pattern = r'\{([^}]+)\}'
    params = re.findall(param_pattern, path)

    filled_path = path
    for param in params:
        value = input(f"Enter value for '{param}': ")
        filled_path = filled_path.replace(f'{{{param}}}', value)

    return filled_path


def fill_path_params_from_references(path: str, context: Dict[str, Any]) -> str:
    """Fill path parameters with references to previous response data."""
    if not context:
        print("No previous response data available. Using manual entry.")
        return fill_path_params_manually(path)

    # Find all parameter placeholders
    param_pattern = r'\{([^}]+)\}'
    params = re.findall(param_pattern, path)

    filled_path = path
    for param in params:
        # Clean parameter name - remove any source reference
        clean_param = param.split('.')[-1] if '.' in param else param

        print(f"\nParameter: {clean_param}")
        print("1. Enter value manually")
        print("2. Reference from previous response")
        choice = input("Enter your choice (1-2): ")

        if choice == "2":
            # For references, we'll create the reference expression, not resolve it now
            # It gets resolved when the request actually runs
            reference = reference_previous_data(clean_param, context)
            if reference:
                filled_path = filled_path.replace(f'{{{param}}}', reference)
            else:
                # Fallback to manual entry
                value = input(f"Enter value for '{clean_param}': ")
                filled_path = filled_path.replace(f'{{{param}}}', value)
        else:
            value = input(f"Enter value for '{clean_param}': ")
            filled_path = filled_path.replace(f'{{{param}}}', value)

    return filled_path


def fill_path_params_randomly(path: str) -> str:
    """Fill path parameters with random values."""
    # Find all parameter placeholders
    param_pattern = r'\{([^}]+)\}'
    params = re.findall(param_pattern, path)

    filled_path = path
    for param in params:
        param_lower = param.lower()

        # Generate appropriate random value based on parameter name
        if 'id' in param_lower:
            value = f"id_{uuid.uuid4().hex[:8]}"
        elif 'user' in param_lower and 'id' in param_lower:
            value = f"user_{random.randint(1000, 9999)}"
        elif 'api' in param_lower and 'id' in param_lower:
            value = f"api_{uuid.uuid4().hex[:6]}"
        elif 'version' in param_lower:
            value = f"v{random.randint(1, 3)}"
        elif 'status' in param_lower:
            value = random.choice(["active", "inactive", "pending"])
        elif any(term in param_lower for term in ['num', 'count', 'index']):
            value = str(random.randint(1, 100))
        else:
            # Default to random string
            value = f"param_{random.randint(100, 999)}"

        filled_path = filled_path.replace(f'{{{param}}}', value)

    return filled_path


def _modify_specific_field(body: Dict[str, Any], field_path: str) -> Dict[str, Any]:
    """Modify a specific field by its path."""
    # Parse the path to handle array indices
    path_parts = []
    current_path = ""

    for char in field_path:
        if char == '[':
            if current_path:
                path_parts.append(current_path)
                current_path = ""
            current_path = char
        elif char == ']':
            current_path += char
            path_parts.append(current_path)
            current_path = ""
        elif char == '.':
            if current_path:
                path_parts.append(current_path)
                current_path = ""
        else:
            current_path += char

    if current_path:
        path_parts.append(current_path)

    # Navigate to the field
    current = body
    for i, part in enumerate(path_parts[:-1]):
        if part.startswith('[') and part.endswith(']'):
            # Handle array index
            index = int(part[1:-1])
            current = current[index]
        else:
            current = current[part]

    # Get the last part
    last_part = path_parts[-1]
    if last_part.startswith('[') and last_part.endswith(']'):
        index = int(last_part[1:-1])
        old_value = current[index]
    else:
        old_value = current[last_part]

    print(f"\nCurrent value of '{field_path}': {old_value}")

    field_type = input("Enter new value type (string/number/boolean/array/object/keep-current): ").lower()

    if field_type == "keep-current":
        return body
    elif field_type == "string":
        new_value = input("Enter new string value: ")
    elif field_type == "number":
        new_value = float(input("Enter new number value: "))
    elif field_type == "boolean":
        new_value = input("Enter new boolean value (true/false): ").lower() == "true"
    elif field_type == "array":
        print("Enter new array items (one per line, empty line to finish):")
        new_value = []
        while True:
            item = input("Item: ")
            if not item:
                break
            new_value.append(_parse_value(item))
    elif field_type == "object":
        new_value = {}
        print("You'll define the new object structure now.")
    else:
        print("Invalid field type.")
        return body

    # Set the new value
    if last_part.startswith('[') and last_part.endswith(']'):
        index = int(last_part[1:-1])
        current[index] = new_value
    else:
        current[last_part] = new_value

    print(f"Field '{field_path}' modified successfully.")
    return body


def _remove_specific_field(body: Dict[str, Any], field_path: str) -> Dict[str, Any]:
    """Remove a specific field by its path."""
    # Parse the path to handle array indices
    path_parts = []
    current_path = ""

    for char in field_path:
        if char == '[':
            if current_path:
                path_parts.append(current_path)
                current_path = ""
            current_path = char
        elif char == ']':
            current_path += char
            path_parts.append(current_path)
            current_path = ""
        elif char == '.':
            if current_path:
                path_parts.append(current_path)
                current_path = ""
        else:
            current_path += char

    if current_path:
        path_parts.append(current_path)

    # Navigate to the parent of the field to remove
    current = body
    for part in path_parts[:-1]:
        if part.startswith('[') and part.endswith(']'):
            index = int(part[1:-1])
            current = current[index]
        else:
            current = current[part]

    # Remove the field
    last_part = path_parts[-1]
    if last_part.startswith('[') and last_part.endswith(']'):
        index = int(last_part[1:-1])
        if isinstance(current, list) and 0 <= index < len(current):
            current.pop(index)
            print(f"Element {index} removed from array successfully.")
        else:
            print(f"Invalid array index.")
    else:
        if last_part in current:
            del current[last_part]
            print(f"Field '{field_path}' removed successfully.")
        else:
            print(f"Field '{field_path}' not found.")

    return body


def _add_body_field(body: Dict[str, Any]) -> Dict[str, Any]:
    """Add a field to the body."""
    path = input("Enter field path (e.g., 'user.name' for nested field): ")
    field_type = input("Enter field type (string/number/boolean/array/object): ").lower()

    if field_type == "string":
        value = input("Enter string value: ")
    elif field_type == "number":
        value = float(input("Enter number value: "))
    elif field_type == "boolean":
        value = input("Enter boolean value (true/false): ").lower() == "true"
    elif field_type == "array":
        print("Enter array items (one per line, empty line to finish):")
        items = []
        while True:
            item = input("Item: ")
            if not item:
                break
            items.append(_parse_value(item))
        value = items
    elif field_type == "object":
        value = {}
        print("You'll define the object structure now.")
    else:
        print("Invalid field type.")
        return body

    # Navigate and create the nested structure
    parts = path.split('.')
    current = body
    for i, part in enumerate(parts[:-1]):
        if part not in current:
            current[part] = {}
        current = current[part]

    current[parts[-1]] = value
    print(f"Field '{path}' added successfully.")
    return body


def _parse_value(value: str) -> Any:
    """Parse string value to appropriate type."""
    try:
        return json.loads(value)
    except:
        return value


# Body template management
def save_body_template(body: Dict[str, Any], body_type: str, template_name: str):
    """Save body template to file."""
    templates_file = "body_templates.json"
    templates = {}

    if os.path.exists(templates_file):
        with open(templates_file, "r") as f:
            templates = json.load(f)

    if body_type not in templates:
        templates[body_type] = {}

    templates[body_type][template_name] = body

    with open(templates_file, "w") as f:
        json.dump(templates, f, indent=2)

    print(f"Template '{template_name}' saved for body type '{body_type}'")


def load_body_templates(body_type: str = None) -> Dict[str, Any]:
    """Load saved body templates."""
    templates_file = "body_templates.json"

    if not os.path.exists(templates_file):
        return {}

    with open(templates_file, "r") as f:
        all_templates = json.load(f)

    if body_type and body_type in all_templates:
        return all_templates[body_type]
    return all_templates


def select_body_template(body_type: str) -> Dict[str, Any]:
    """Allow user to select a saved body template."""
    templates = load_body_templates(body_type)

    if not templates:
        print(f"No saved templates for body type '{body_type}'")
        return None

    print(f"\nAvailable templates for '{body_type}':")
    template_names = list(templates.keys())
    for i, name in enumerate(template_names, 1):
        print(f"{i}. {name}")

    choice = input("\nSelect template (enter number or 'n' for new): ")

    if choice.isdigit() and 1 <= int(choice) <= len(template_names):
        selected_name = template_names[int(choice) - 1]
        return templates[selected_name].copy()

    return None


def extract_fields_from_schema(schema: Dict[str, Any]) -> List[str]:
    """Extract field paths from a JSON schema definition."""
    fields = []

    def extract_from_object(obj_schema: Dict[str, Any], prefix: str = "") -> None:
        if 'properties' in obj_schema:
            for prop_name, prop_schema in obj_schema['properties'].items():
                field_path = f"{prefix}.{prop_name}" if prefix else prop_name
                fields.append(field_path)

                if prop_schema.get('type') == 'object':
                    extract_from_object(prop_schema, field_path)
                elif prop_schema.get('type') == 'array' and 'items' in prop_schema:
                    items_schema = prop_schema['items']
                    if items_schema.get('type') == 'object':
                        extract_from_object(items_schema, f"{field_path}[0]")

    extract_from_object(schema)
    return fields


def add_field_from_path(body: Dict[str, Any], field_path: str, available_saved_data: Dict[str, Any] = None) -> Dict[
    str, Any]:
    """Add a field to the body using a specific path."""
    print(f"\nAdding field: {field_path}")

    field_type_options = [
        "string",
        "number",
        "boolean",
        "array",
        "object",
        "random",  # Let system generate random value
        "reference"  # Reference data from previous response
    ]

    print("Enter field type:")
    for i, option in enumerate(field_type_options, 1):
        print(f"{i}. {option}")

    type_choice = input("Enter choice (1-7): ")

    try:
        field_type = field_type_options[int(type_choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice. Using 'string' as default.")
        field_type = "string"

    if field_type == "string":
        value = input("Enter string value: ")
    elif field_type == "number":
        value = float(input("Enter number value: "))
    elif field_type == "boolean":
        value = input("Enter boolean value (true/false): ").lower() == "true"
    elif field_type == "array":
        print("Enter array items (one per line, empty line to finish):")
        items = []
        while True:
            item = input("Item: ")
            if not item:
                break
            items.append(_parse_value(item))
        value = items
    elif field_type == "object":
        value = {}
        print("Empty object created.")
    elif field_type == "random":
        # Generate random value based on field name/pattern
        value = generate_random_value_for_field(field_path)
        print(f"Generated random value: {value}")
    elif field_type == "reference":
        value = reference_previous_data(field_path, available_saved_data)
    else:
        print("Invalid field type.")
        return body

    # Navigate and create the nested structure
    parts = field_path.split('.')
    current = body
    for i, part in enumerate(parts[:-1]):
        # Handle array notation
        if '[' in part and ']' in part:
            field_name = part[:part.index('[')]
            if field_name not in current:
                current[field_name] = []
            current = current[field_name]
            # Ensure array has enough elements
            while len(current) <= 0:
                current.append({})
            current = current[0]
        else:
            if part not in current:
                current[part] = {}
            current = current[part]

    current[parts[-1]] = value
    print(f"Field '{field_path}' added successfully.")
    return body


# Add this new function
def fill_remaining_fields_with_random_data(user_body: Dict[str, Any], full_body: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user-provided fields with random data for remaining fields."""
    result = full_body.copy()

    def merge_nested(user: Dict[str, Any], full: Dict[str, Any], result: Dict[str, Any]):
        for key, value in full.items():
            if key in user:
                if isinstance(user[key], dict) and isinstance(value, dict):
                    # Recursively merge nested objects
                    result[key] = {}
                    merge_nested(user[key], value, result[key])
                else:
                    # Use user's value
                    result[key] = user[key]
            else:
                # Keep random/auto-generated value
                result[key] = value

    merge_nested(user_body, full_body, result)
    return result


def reference_previous_data(field_path: str, available_saved_data: Dict[str, Any]) -> Any:
    """Reference data from previous API responses."""
    if not available_saved_data:
        print("No previous response data available.")
        return None

    print("\nAvailable saved data:")
    saved_keys = list(available_saved_data.keys())
    for i, key in enumerate(saved_keys, 1):
        print(f"{i}. {key}")

    source_choice = input("Select source data (enter number): ")
    try:
        source_key = saved_keys[int(source_choice) - 1]
        source_data = available_saved_data[source_key]

        # Check if it's still a placeholder
        if source_data.get("_placeholder"):
            print(
                f"\nNote: '{source_key}' is still a placeholder. The actual data will be available after the request runs.")
            print("Creating reference anyway...")

            # For common patterns, suggest the likely field name
            if "id" in field_path.lower() or "apiid" in field_path.lower():
                suggested_field = "id"
            elif "version" in field_path.lower():
                suggested_field = "version"
            else:
                suggested_field = None

            if suggested_field:
                print(f"Suggested field: {suggested_field}")
                use_suggested = input(f"Use '{suggested_field}'? (y/n): ").lower()
                if use_suggested == 'y':
                    field_to_reference = suggested_field
                else:
                    field_to_reference = input("Enter field name: ")
            else:
                field_to_reference = input("Enter field name: ")
        else:
            # Normal flow for actual data
            print(f"\nFields available in '{source_key}':")
            fields = get_all_field_paths(source_data)
            for i, field in enumerate(fields, 1):
                print(f"{i}. {field}")

            field_choice = input("Select field to reference (enter number): ")
            field_to_reference = fields[int(field_choice) - 1]

        # Create reference expression
        reference_expr = f"${{{source_key}.{field_to_reference}}}"
        print(f"Created reference: {reference_expr}")

        return reference_expr
    except (ValueError, IndexError):
        print("Invalid choice. Using null value.")
        return None

# Modify enhanced_body_creation function
def enhanced_body_creation(method: str, path: str, body: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[
    str, Any]:
    """Enhanced body creation with templates and customization."""
    endpoint_type = path.split("/")[0]

    # Get validator to generate full body with random data
    validator = ValidatorFactory.get_validator(endpoint_type)
    full_body_with_random = None

    if validator and hasattr(validator, 'get_valid_body'):
        full_body_with_random = validator.get_valid_body()

    if body is None:
        # Show available fields for this endpoint
        fields_info = []
        if full_body_with_random:
            fields_info = get_all_field_paths(full_body_with_random)

        print("\nBody Creation Options:")
        print("1. Generate automatically (all fields with random data)")
        print("2. Load from saved template")
        print("3. Add specific fields (others will be filled randomly)")

        if fields_info:
            print(f"\nNote: '{endpoint_type}' endpoint has these fields:")
            for i, field in enumerate(fields_info, 1):
                print(f"  {i}. {field}")

        choice = input("\nEnter your choice (1-3): ")

        if choice == "1":
            # Generate with validator (all random)
            body = full_body_with_random if full_body_with_random else {}
        elif choice == "2":
            # Try to load template
            body = select_body_template(endpoint_type)
            if body is None:
                body = {}
        else:
            # Create from scratch with specific fields
            body = {}

            # Get user's custom fields
            user_body = customize_body_fields(body, endpoint_type, context)

            # Merge with full random body
            if user_body and full_body_with_random:
                print("\nMerging your fields with random data for remaining fields...")
                body = fill_remaining_fields_with_random_data(user_body, full_body_with_random)
            else:
                body = user_body
    else:
        # If body already exists, offer customization
        body = customize_body_fields(body, endpoint_type, context)

    # Validate before returning
    if validator and hasattr(validator, 'validate'):
        try:
            validator.validate(body)
            print("Body validation: PASSED")
        except Exception as e:
            print(f"Body validation: FAILED - {e}")
            if input("Continue with invalid body? (y/n): ").lower() != 'y':
                return None

    return body


# Update the customize_body_fields for empty bodies when user wants to add specific fields
def customize_body_fields(body: Dict[str, Any], body_type: str = None, context: Dict[str, Any] = None) -> Dict[
    str, Any]:
    """Allow users to manually add or modify body fields after auto-generation."""
    if not body:  # Handle empty body - user wants to add specific fields
        # Get sample body to show available fields
        validator = ValidatorFactory.get_validator(body_type)
        fields_to_show = []

        if validator and hasattr(validator, 'get_valid_body'):
            sample_body = validator.get_valid_body()
            fields_to_show = get_all_field_paths(sample_body)

        if fields_to_show:
            print(f"\nAvailable fields for '{body_type}':")
            for i, field in enumerate(fields_to_show, 1):
                print(f"{i}. {field}")

            print("\nWould you like to add specific fields?")
            print("1. Add specific field(s)")
            print("2. Skip (all fields will be filled with random data)")
            choice = input("Enter your choice (1-2): ")

            if choice == "1":
                # Let user add fields one by one
                while True:
                    field_num = input("\nEnter field number to add (or press Enter to finish): ")
                    if not field_num:
                        break

                    try:
                        num = int(field_num)
                        if 1 <= num <= len(fields_to_show):
                            field_path = fields_to_show[num - 1]
                            body = add_field_from_path(body, field_path, context)
                        else:
                            print("Invalid field number.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")

                    # Ask if they want to add more
                    if input("Add another field? (y/n): ").lower() != 'y':
                        break
        else:
            print(f"\nNo field information available for '{body_type}'.")
            print("Fields will be filled with random data.")

        return body

    # Rest of the method remains the same for non-empty bodies...
    print("\nWould you like to customize the request body?")
    print("1. View current body fields")
    print("2. Add/modify fields")
    print("3. Skip customization")
    choice = input("Enter your choice (1-3): ")

    if choice == "1":
        print("\nCurrent body fields:")
        fields = get_all_field_paths(body)
        for i, field in enumerate(fields, 1):
            print(f"{i}. {field}")

        print("\nEnter field numbers to modify (comma-separated), or press Enter to go back:")
        field_input = input("Field numbers: ").strip()

        if field_input:
            try:
                field_numbers = [int(x.strip()) for x in field_input.split(',')]
                for num in field_numbers:
                    if 1 <= num <= len(fields):
                        field_path = fields[num - 1]
                        body = _modify_specific_field(body, field_path)
            except ValueError:
                print("Invalid input. Please enter valid numbers.")

        return body
    elif choice == "2":
        print("\nBody Customization Options:")
        print("1. Add a field")
        print("2. Modify existing field")
        print("3. Remove a field")
        print("4. List all fields")
        print("5. Finish customization")

        while True:
            sub_choice = input("\nEnter your choice (1-5): ")

            if sub_choice == "1":
                body = add_field_from_path(body, "", context)
            elif sub_choice == "2":
                # List fields and let user select by number
                fields = get_all_field_paths(body)
                if fields:
                    print("\nAvailable fields:")
                    for i, field in enumerate(fields, 1):
                        print(f"{i}. {field}")
                    field_num = input("\nEnter field number to modify: ")
                    try:
                        num = int(field_num)
                        if 1 <= num <= len(fields):
                            field_path = fields[num - 1]
                            body = _modify_specific_field(body, field_path)
                        else:
                            print("Invalid field number.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                else:
                    print("No fields available.")
            elif sub_choice == "3":
                # List fields and let user select by number to remove
                fields = get_all_field_paths(body)
                if fields:
                    print("\nAvailable fields:")
                    for i, field in enumerate(fields, 1):
                        print(f"{i}. {field}")
                    field_num = input("\nEnter field number to remove: ")
                    try:
                        num = int(field_num)
                        if 1 <= num <= len(fields):
                            field_path = fields[num - 1]
                            body = _remove_specific_field(body, field_path)
                        else:
                            print("Invalid field number.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                else:
                    print("No fields available.")
            elif sub_choice == "4":
                print("\nAvailable fields:")
                fields = get_all_field_paths(body)
                for i, field in enumerate(fields, 1):
                    print(f"{i}. {field}")
            elif sub_choice == "5":
                break
            else:
                print("Invalid choice, please try again.")

        # Ask if user wants to save this body template
        save_choice = input("\nSave this body structure for future use? (y/n): ").lower()
        if save_choice == 'y':
            template_name = input("Enter template name: ")
            save_body_template(body, body_type, template_name)

    return body


def generate_random_value_for_field(field_path: str) -> Any:
    """Generate random value based on field name/pattern."""
    field_name = field_path.split('.')[-1].lower()

    # Common field name patterns
    if 'id' in field_name:
        return f"id_{uuid.uuid4().hex[:8]}"
    elif 'name' in field_name:
        return f"name_{random.randint(1, 999)}"
    elif 'email' in field_name:
        return f"user{random.randint(1, 999)}@example.com"
    elif 'url' in field_name:
        return f"https://example-{random.randint(1, 999)}.com"
    elif 'status' in field_name:
        return random.choice(["ACTIVE", "INACTIVE", "PENDING"])
    elif 'description' in field_name:
        return f"Auto-generated description {random.randint(1, 999)}"
    elif 'version' in field_name:
        return f"v{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
    elif 'context' in field_name:
        return f"/api/{random.choice(['v1', 'v2'])}/{field_name}"
    elif any(term in field_name for term in ['count', 'num', 'size']):
        return random.randint(1, 100)
    elif any(term in field_name for term in ['is', 'has', 'enable']):
        return random.choice([True, False])
    elif 'type' in field_name:
        return random.choice(["API", "SERVICE", "GATEWAY", "ENDPOINT"])
    elif 'tags' in field_name:
        tags = ["prod", "dev", "test", "qa", "api", "v1", "v2", "internal", "external"]
        return random.sample(tags, random.randint(1, 3))
    elif 'date' in field_name or 'time' in field_name:
        return datetime.datetime.utcnow().isoformat() + "Z"
    else:
        # Default to string
        return f"auto_{random.randint(1000, 9999)}"


def create_new_scenario():
    """Prompts the user to create a new test scenario."""
    scenario_name = input("Enter scenario name: ")
    scenario_id = input("Enter scenario ID: ")
    scenario_description = input("Enter scenario description: ")
    scenario_version = input("Enter scenario version: ")
    now = datetime.datetime.utcnow().isoformat() + "Z"
    requests = []
    context = {}  # Track saved data across requests

    num_endpoints = int(input("Enter the number of endpoints in this scenario: "))

    for i in range(num_endpoints):
        print(f"\n--- Endpoint {i + 1} ---")
        request_name = input("Enter request name: ")
        method = input("Enter HTTP method (GET/POST/PUT/DELETE/...): ").upper()
        path_input = input("Enter endpoint path (e.g., 'api-specs/{apiId}/versions/{versionId}'): ").strip().lstrip("/")

        # Handle path parameters
        path = handle_path_parameters(path_input, context)
        url = f"{LOCALDEV_BASE_URL}/{path}"

        print(f"Final URL: {url}")

        # Generate valid request body based on the endpoint type
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            # Pass context to enhanced_body_creation
            body = enhanced_body_creation(method, path, None, context)

            # Display final body if not None
            if body:
                print("\nFinal request body:")
                print(json.dumps(body, indent=2))

        save_as = input("Enter a name to save the response data (or leave empty): ")

        # Update context if save_as is provided (for future references)
        if save_as:
            # We'll store a placeholder that gets filled when the request actually runs
            context[save_as] = {"_placeholder": True}

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