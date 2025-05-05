import yaml
from typing import Any, Type

def object_to_yaml_file(obj: Any, file_path: str) -> None:
    try:
        data = obj.to_dict() if hasattr(obj, "to_dict") else obj
        with open(file_path, 'w') as file:
            yaml.safe_dump(data, file)
    except Exception as e:
        raise ValueError(f"Error converting object to YAML file: {e}")

def yaml_file_to_object(file_path: str, obj_type: Type) -> Any:
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            return obj_type.from_dict(data) if hasattr(obj_type, "from_dict") else obj_type(**data)
    except yaml.YAMLError as e:
        raise ValueError(f"Error converting YAML file to object: {e}")
    except TypeError as e:
        raise ValueError(f"Error initializing object of type {obj_type}: {e}")

def is_yaml_exists(file_path: str) -> bool:
    """
    Check if a YAML file exists.
    """
    try:
        with open(file_path, 'r') as file:
            return True
    except FileNotFoundError:
        return False
    except Exception as e:
        raise ValueError(f"Error checking if YAML file exists: {e}")