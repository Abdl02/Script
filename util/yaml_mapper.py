import yaml
from typing import Any, Type

def object_to_yaml_file(obj: Any, file_path: str) -> None:
    """
    Serialize an object to a YAML file as a plain dictionary.
    """
    try:
        # Convert the object to a dictionary if it has a `to_dict` method
        data = obj.to_dict() if hasattr(obj, "to_dict") else obj
        with open(file_path, 'w') as file:
            yaml.safe_dump(data, file)
    except Exception as e:
        raise ValueError(f"Error converting object to YAML file: {e}")

def yaml_file_to_object(file_path: str, obj_type: Type) -> Any:
    """
    Deserialize a YAML file into an object of the specified type.
    """
    try:
        with open(file_path, 'r') as file:
            # Load the YAML data as a dictionary
            data = yaml.safe_load(file)
            # Dynamically create an instance of the specified type if it has a `from_dict` method
            return obj_type.from_dict(data) if hasattr(obj_type, "from_dict") else obj_type(**data)
    except yaml.YAMLError as e:
        raise ValueError(f"Error converting YAML file to object: {e}")
    except TypeError as e:
        raise ValueError(f"Error initializing object of type {obj_type}: {e}")