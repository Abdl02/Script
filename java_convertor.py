import os
import re

def convert_java_to_python(java_code):
    # Remove package and import statements
    java_code = re.sub(r'package\s+[^;]+;', '', java_code)
    java_code = re.sub(r'import\s+[^;]+;', '', java_code)
    
    # Check if it's an enum
    enum_match = re.search(r'public\s+enum\s+(\w+)', java_code)
    if enum_match:
        return convert_enum_to_python(java_code, enum_match.group(1))
    
    # Check if it's a utility class with only static methods
    utility_class_match = re.search(r'public\s+(?:final\s+)?class\s+(\w+)', java_code)
    if utility_class_match and "private" in java_code and "static" in java_code:
        class_name = utility_class_match.group(1)
        if re.search(r'private\s+'+class_name+r'\(\)', java_code):
            return convert_utility_class_to_python(java_code, class_name)
    
    # Extract the main class and any nested classes
    all_classes = extract_classes(java_code)
    
    python_output = ""
    
    for class_info in all_classes:
        class_name = class_info['name']
        class_code = class_info['code']
        is_nested = class_info['is_nested']
        
        # Check for Lombok annotations
        has_builder = "@Builder" in class_code
        has_all_args_constructor = "@AllArgsConstructor" in class_code
        has_no_args_constructor = "@NoArgsConstructor" in class_code
        
        # Find static constants
        static_constants = extract_static_constants(class_code)
        
        # Extract fields with their annotations
        fields = extract_fields_with_annotations(class_code)
        
        # Generate Python class
        class_prefix = "    " if is_nested else ""
        python_class = f"{class_prefix}class {class_name}:\n"
        
        # Add static constants
        for constant in static_constants:
            name, value, type_name = constant
            python_class += f"{class_prefix}    {name} = {value}  # {type_name}\n"
        
        if static_constants:
            python_class += "\n"
        
        # Generate constructor
        if has_no_args_constructor or len(fields) > 0:
            python_class += f"{class_prefix}    def __init__(self):\n"
            
            if len(fields) > 0:
                for field_info in fields:
                    field_name = field_info['name']
                    field_type = field_info['type']
                    field_annotations = field_info['annotations']
                    
                    # Add comment with type and annotations
                    annotation_comment = ""
                    if field_annotations:
                        annotation_comment = f" # {' '.join(field_annotations)}"
                    
                    # Check if it might be an enum
                    enum_comment = ""
                    if (field_type[0].isupper() and 
                        field_type not in ["String", "Integer", "Long", "Double", "Boolean", "LocalDateTime"] and
                        not field_type.startswith(("Map<", "List<", "Set<"))):
                        enum_comment = "  # This might be an enum"
                    
                    python_class += f"{class_prefix}        self.{field_name} = None  # {field_type}{annotation_comment}{enum_comment}\n"
            else:
                python_class += f"{class_prefix}        pass\n"
                
        # Generate getter and setter methods
        getter_setter_code = ""
        for field_info in fields:
            field_name = field_info['name']
            if "@Getter" in field_info['annotations']:
                getter_setter_code += f"\n{class_prefix}    def get_{field_name}(self):\n"
                getter_setter_code += f"{class_prefix}        return self.{field_name}\n"
            
            if "@Setter" in field_info['annotations']:
                getter_setter_code += f"\n{class_prefix}    def set_{field_name}(self, value):\n"
                getter_setter_code += f"{class_prefix}        self.{field_name} = value\n"
        
        if getter_setter_code:
            python_class += getter_setter_code
        
        python_output += python_class + "\n\n" if not is_nested else python_class
    
    return python_output.rstrip()

def extract_classes(java_code):
    # Find all class definitions (including nested ones)
    class_pattern = r'(?:@[\w\s\(\)\",.=]+\s+)*(?:public|private|protected)?\s+(?:static\s+)?class\s+(\w+)(?:[^{]*)\{((?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*)\}'
    classes = []
    
    # First extract the main class
    main_class_match = re.search(class_pattern, java_code, re.DOTALL)
    if main_class_match:
        main_class_name = main_class_match.group(1)
        main_class_body = main_class_match.group(2)
        
        classes.append({
            'name': main_class_name,
            'code': main_class_body,
            'is_nested': False
        })
        
        # Look for nested classes within the main class
        nested_class_matches = re.finditer(class_pattern, main_class_body, re.DOTALL)
        for match in nested_class_matches:
            nested_class_name = match.group(1)
            nested_class_body = match.group(2)
            
            classes.append({
                'name': nested_class_name,
                'code': nested_class_body,
                'is_nested': True
            })
    
    return classes

def extract_static_constants(class_code):
    # Find static final constants
    const_pattern = r'(?:public|private|protected)\s+static\s+final\s+(\w+(?:<.*?>)?)\s+(\w+)\s*=\s*"?([^;]+?)"?;'
    constants = re.findall(const_pattern, class_code)
    return constants  # Returns list of tuples: (name, value, type)

def extract_fields_with_annotations(class_code):
    # First, split the code into lines to handle annotation processing
    lines = class_code.split('\n')
    
    fields = []
    current_annotations = []
    
    for line in lines:
        line = line.strip()
        
        # Check if line is an annotation
        if line.startswith('@'):
            annotation = line.split('(')[0][1:]  # Extract annotation name without params
            current_annotations.append('@' + annotation)
            continue
            
        # Check if line is a field declaration
        field_match = re.search(r'(?:private|protected|public)\s+(\w+(?:<.*?>)?)\s+(\w+)\s*;', line)
        if field_match:
            field_type = field_match.group(1)
            field_name = field_match.group(2)
            
            fields.append({
                'name': field_name,
                'type': field_type,
                'annotations': current_annotations.copy()
            })
            
            # Reset annotations for next field
            current_annotations = []
    
    return fields

def convert_enum_to_python(java_code, enum_name):
    # Extract enum constants
    enum_constants_match = re.search(fr'enum\s+{enum_name}\s*\{{(.*?)\}}', java_code, re.DOTALL)
    if not enum_constants_match:
        return f"class {enum_name}:\n    pass  # Enum conversion failed"
    
    enum_constants_str = enum_constants_match.group(1)
    
    # Extract each constant, handling possible trailing methods or semicolons
    constants = []
    for item in re.split(r',\s*', enum_constants_str):
        item = item.strip()
        if item and not item.startswith(('(', '@', '/')):
            constant = item.split('(')[0].split(';')[0].strip()
            if constant:
                constants.append(constant)
    
    # Generate Python enum class
    python_enum = f"class {enum_name}:\n"
    
    # Add enum constants as class variables
    for i, constant in enumerate(constants):
        python_enum += f"    {constant} = {i}\n"
    
    # Add fromValue method if exists in Java
    if "fromValue" in java_code:
        python_enum += "\n    @classmethod\n"
        python_enum += f"    def fromValue(cls, value):\n"
        python_enum += f"        if not value:\n"
        python_enum += f"            raise ValueError(\"Empty enum value\")\n"
        python_enum += f"        try:\n"
        python_enum += f"            return getattr(cls, value)\n"
        python_enum += f"        except AttributeError:\n"
        python_enum += f"            raise ValueError(f\"Invalid {enum_name} value: {{value}}\")\n"
    
    return python_enum

def convert_utility_class_to_python(java_code, class_name):
    """
    Converts a Java utility class with static methods to a Python class with class methods.
    """
    # First, extract static constants
    const_pattern = r'(?:public|private|protected)\s+static\s+final\s+(\w+(?:<.*?>)?)\s+(\w+)\s*=\s*"?([^;]+?)"?;'
    constants = re.findall(const_pattern, java_code)
    
    # Extract static methods
    method_pattern = r'(?:public|private|protected)\s+static\s+(\w+(?:<.*?>)?)\s+(\w+)\s*\((.*?)\)\s*\{((?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*)\}'
    methods = re.findall(method_pattern, java_code, re.DOTALL)
    
    # Generate Python utility class
    python_class = f"class {class_name}:\n"
    
    # Add class constants
    for type_name, name, value in constants:
        python_class += f"    {name} = {value}  # {type_name}\n"
    
    if constants:
        python_class += "\n"
    
    # Add static methods as class methods
    for return_type, method_name, params, body in methods:
        # Convert parameters
        param_list = params.strip()
        python_params = []
        
        if param_list:
            java_params = re.findall(r'(?:final\s+)?(\w+(?:<.*?>)?)\s+(\w+)(?:,|$)', param_list)
            for _, param_name in java_params:
                python_params.append(param_name)
        
        # Convert method body to Python-style comments (simplified)
        # This is a simple conversion - in a real implementation, we would parse and convert the Java code
        body_lines = body.strip().split('\n')
        indented_body = ["        # " + line.strip() for line in body_lines]
        
        # Generate Python method
        python_class += f"    @classmethod\n"
        python_class += f"    def {method_name}(cls, {', '.join(python_params)}):\n"
        python_class += f"        \"\"\"Java method: {return_type} {method_name}({params})\"\"\"\n"
        
        if indented_body:
            python_class += '\n'.join(indented_body) + "\n"
            python_class += "        pass  # Implementation needed\n\n"
        else:
            python_class += "        pass  # Implementation needed\n\n"
    
    return python_class

def convert_all_java_to_python(directory):
    for root, dirs, files in os.walk(directory):  # Correctly unpack the os.walk() tuple
        for file_name in files:
            if file_name.endswith(".java"):
                java_file_path = os.path.join(root, file_name)
                with open(java_file_path, 'r') as java_file:
                    java_code = java_file.read()
                try:
                    python_code = convert_java_to_python(java_code)
                    python_file_path = os.path.splitext(java_file_path)[0] + ".py"
                    with open(python_file_path, 'w') as python_file:
                        python_file.write(python_code)
                    print(f"Converted: {java_file_path} -> {python_file_path}")
                except ValueError as e:
                    print(f"Skipping {java_file_path}: {e}")

# Run the script in the current directory
if __name__ == "__main__":
    current_directory = os.getcwd()
    convert_all_java_to_python(current_directory)