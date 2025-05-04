"""
Random data generator for filling test data with valid values
"""
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Type
from enum import Enum
import json


class DataType(Enum):
    """Data types for validation"""
    STRING = "string"
    INTEGER = "integer"
    LONG = "long"
    FLOAT = "float"
    DOUBLE = "double"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    URL = "url"
    UUID = "uuid"
    PHONE = "phone"
    JSON = "json"
    ENUM = "enum"
    ARRAY = "array"
    OBJECT = "object"
    IP_ADDRESS = "ip_address"


class RandomDataFactory:
    """
    Factory class for generating random valid data based on field specifications
    """

    def __init__(self):
        self.faker_like_data = {
            "first_names": ["John", "Jane", "Michael", "Sarah", "David", "Emma", "Robert", "Lisa"],
            "last_names": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"],
            "companies": ["Acme Corp", "Tech Solutions", "Global Industries", "Innovation Labs"],
            "domains": ["example.com", "test.org", "demo.net", "sample.io", "digitinary.com"],
            "streets": ["Main St", "Oak Ave", "Pine St", "Maple Ave", "Cedar St"],
            "cities": ["New York", "London", "Tokyo", "Paris", "Dubai", "Singapore"],
            "job_titles": ["Manager", "Director", "Engineer", "Analyst", "Consultant", "Specialist"]
        }

    def generate_random_string(self, min_length: int = 8, max_length: int = 20,
                               pattern: Optional[str] = None) -> str:
        """Generate a random string with given constraints"""
        if pattern:
            if pattern.startswith("uuid"):
                return str(uuid.uuid4())
            elif pattern.startswith("email"):
                return self.generate_email()
            elif pattern.startswith("phone"):
                return self.generate_phone()
            elif pattern.startswith("url"):
                return self.generate_url()

        length = random.randint(min_length, max_length)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def generate_email(self) -> str:
        """Generate a valid email address"""
        name = self.generate_name().lower().replace(" ", ".")
        domain = random.choice(self.faker_like_data["domains"])
        return f"{name}@{domain}"

    def generate_phone(self) -> str:
        """Generate a valid phone number"""
        # Generate a simple format: +X-XXX-XXX-XXXX
        area_code = random.randint(100, 999)
        number = random.randint(1000000, 9999999)
        return f"+1-{area_code}-{str(number)[:3]}-{str(number)[3:]}"

    def generate_url(self, protocol: str = "https") -> str:
        """Generate a valid URL"""
        domain = random.choice(self.faker_like_data["domains"])
        path = f"/{self.generate_random_string(5, 10)}"
        return f"{protocol}://{domain}{path}"

    def generate_name(self) -> str:
        """Generate a random person name"""
        first = random.choice(self.faker_like_data["first_names"])
        last = random.choice(self.faker_like_data["last_names"])
        return f"{first} {last}"

    def generate_company_name(self) -> str:
        """Generate a random company name"""
        return random.choice(self.faker_like_data["companies"])

    def generate_ip_address(self, v4: bool = True) -> str:
        """Generate a valid IP address"""
        if v4:
            return ".".join(str(random.randint(0, 255)) for _ in range(4))
        else:
            # IPv6
            parts = [format(random.randint(0, 65535), 'x') for _ in range(8)]
            return ":".join(parts[:8])

    def generate_date(self, min_year: int = 2020, max_year: int = 2025) -> str:
        """Generate a valid date string"""
        year = random.randint(min_year, max_year)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Simplified to avoid month-specific logic
        return f"{year}-{month:02d}-{day:02d}"

    def generate_datetime(self) -> str:
        """Generate a valid datetime string"""
        date = self.generate_date()
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return f"{date}T{hour:02d}:{minute:02d}:{second:02d}Z"

    def generate_json_value(self, depth: int = 0, max_depth: int = 3) -> Union[Dict, List, str, int, bool]:
        """Generate random JSON-compatible value"""
        if depth >= max_depth:
            return self.generate_primitive_value()

        types = ["object", "array", "primitive"]
        weights = [0.4, 0.3, 0.3] if depth < max_depth - 1 else [0.1, 0.1, 0.8]
        choice = random.choices(types, weights=weights)[0]

        if choice == "object":
            return self.generate_json_object(depth + 1, max_depth)
        elif choice == "array":
            return self.generate_json_array(depth + 1, max_depth)
        else:
            return self.generate_primitive_value()

    def generate_json_object(self, depth: int, max_depth: int) -> Dict:
        """Generate a random JSON object"""
        obj = {}
        num_keys = random.randint(1, 5)
        for _ in range(num_keys):
            key = self.generate_random_string(3, 10)
            value = self.generate_json_value(depth, max_depth)
            obj[key] = value
        return obj

    def generate_json_array(self, depth: int, max_depth: int) -> List:
        """Generate a random JSON array"""
        array = []
        length = random.randint(1, 5)
        for _ in range(length):
            value = self.generate_json_value(depth, max_depth)
            array.append(value)
        return array

    def generate_primitive_value(self) -> Union[str, int, float, bool]:
        """Generate a random primitive value"""
        types = ["string", "integer", "float", "boolean"]
        choice = random.choice(types)

        if choice == "string":
            return self.generate_random_string(5, 15)
        elif choice == "integer":
            return random.randint(1, 1000)
        elif choice == "float":
            return round(random.uniform(1.0, 100.0), 2)
        else:
            return random.choice([True, False])

    def generate_value_by_type(self, data_type: str, constraints: Dict[str, Any] = None) -> Any:
        """Generate a value based on specific data type"""
        constraints = constraints or {}

        if data_type == DataType.STRING.value:
            return self.generate_random_string(
                constraints.get("min_length", 1),
                constraints.get("max_length", 50),
                constraints.get("pattern")
            )

        elif data_type == DataType.INTEGER.value:
            min_val = constraints.get("min", 0)
            max_val = constraints.get("max", 100000)
            return random.randint(min_val, max_val)

        elif data_type == DataType.LONG.value:
            min_val = constraints.get("min", 0)
            max_val = constraints.get("max", 9223372036854775807)
            return random.randint(min_val, max_val)

        elif data_type == DataType.FLOAT.value or data_type == DataType.DOUBLE.value:
            min_val = constraints.get("min", 0.0)
            max_val = constraints.get("max", 100000.0)
            return round(random.uniform(min_val, max_val), 2)

        elif data_type == DataType.BOOLEAN.value:
            return random.choice([True, False])

        elif data_type == DataType.DATE.value:
            return self.generate_date()

        elif data_type == DataType.DATETIME.value:
            return self.generate_datetime()

        elif data_type == DataType.EMAIL.value:
            return self.generate_email()

        elif data_type == DataType.URL.value:
            return self.generate_url()

        elif data_type == DataType.UUID.value:
            return str(uuid.uuid4())

        elif data_type == DataType.PHONE.value:
            return self.generate_phone()

        elif data_type == DataType.JSON.value:
            return self.generate_json_value()

        elif data_type == DataType.IP_ADDRESS.value:
            return self.generate_ip_address()

        elif data_type == DataType.ENUM.value:
            values = constraints.get("values", ["OPTION_1", "OPTION_2", "OPTION_3"])
            return random.choice(values)

        elif data_type == DataType.ARRAY.value:
            item_type = constraints.get("item_type", DataType.STRING.value)
            length = random.randint(constraints.get("min_length", 1), constraints.get("max_length", 5))
            return [self.generate_value_by_type(item_type, constraints.get("item_constraints", {}))
                    for _ in range(length)]

        elif data_type == DataType.OBJECT.value:
            schema = constraints.get("schema", {})
            obj = {}
            for field, field_type in schema.items():
                obj[field] = self.generate_value_by_type(field_type["type"], field_type.get("constraints", {}))
            return obj

        else:
            return self.generate_random_string()

    def fill_template(self, template: Dict[str, Any], field_specs: Dict[str, Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fill a template object with random valid data"""
        result = {}
        field_specs = field_specs or {}

        for key, value in template.items():
            if value is None or value == "":
                # Use field specifications if available
                spec = field_specs.get(key, {})
                data_type = spec.get("type", DataType.STRING.value)
                constraints = spec.get("constraints", {})
                result[key] = self.generate_value_by_type(data_type, constraints)
            elif isinstance(value, dict):
                result[key] = self.fill_template(value, field_specs.get(key, {}))
            elif isinstance(value, list):
                result[key] = [self.fill_template(item, field_specs.get(key, {})) if isinstance(item, dict) else item
                               for item in value]
            else:
                result[key] = value

        return result


# Usage Example
if __name__ == "__main__":
    factory = RandomDataFactory()

    # Example template for an API specification
    api_spec_template = {
        "name": "",  # Will be filled with random string
        "description": "",
        "contextPath": "",
        "backendServiceUrl": "",
        "status": "",
        "type": "",
        "style": "",
        "authType": "",
        "metaData": {
            "version": "",
            "owner": "",
            "createdDateTime": "",
            "tags": []
        },
        "apiSpecRoutes": []
    }

    # Field specifications
    field_specs = {
        "name": {
            "type": DataType.STRING.value,
            "constraints": {"min_length": 5, "max_length": 20}
        },
        "contextPath": {
            "type": DataType.STRING.value,
            "constraints": {"pattern": "/path"}
        },
        "backendServiceUrl": {
            "type": DataType.URL.value
        },
        "status": {
            "type": DataType.ENUM.value,
            "constraints": {"values": ["DRAFT", "PUBLISHED", "UNPUBLISHED", "DELETED"]}
        },
        "type": {
            "type": DataType.ENUM.value,
            "constraints": {"values": ["PUBLIC", "PRIVATE", "PARTNER"]}
        },
        "style": {
            "type": DataType.ENUM.value,
            "constraints": {"values": ["REST", "SOAP", "WEB_SOCKET", "GRPC"]}
        },
        "authType": {
            "type": DataType.ENUM.value,
            "constraints": {"values": ["BASIC", "OAUTH", "API_KEY"]}
        },
        "metaData": {
            "version": {"type": DataType.STRING.value, "constraints": {"pattern": "version"}},
            "owner": {"type": DataType.STRING.value, "constraints": {"min_length": 5}},
            "createdDateTime": {"type": DataType.DATETIME.value},
            "tags": {
                "type": DataType.ARRAY.value,
                "constraints": {
                    "min_length": 1,
                    "max_length": 5,
                    "item_type": DataType.STRING.value,
                    "item_constraints": {"min_length": 3, "max_length": 10}
                }
            }
        }
    }

    # Fill the template with random data
    filled_data = factory.fill_template(api_spec_template, field_specs)
    print(json.dumps(filled_data, indent=2))