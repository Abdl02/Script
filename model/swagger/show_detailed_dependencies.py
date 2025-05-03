import json
import re

def extract_dependent_params(schema):
    dependent_params = []
    if 'properties' in schema:
        for prop, prop_info in schema['properties'].items():
            if '$ref' in prop_info:
                ref = prop_info['$ref']
                schema_name = ref.replace('#/components/schemas/', '')
                dependent_params.append(f"{schema_name}.{prop}")
            elif 'items' in prop_info and '$ref' in prop_info['items']:
                ref = prop_info['items']['$ref']
                schema_name = ref.replace('#/components/schemas/', '')
                dependent_params.append(f"{schema_name}[].{prop}")
    return dependent_params

# Read the Swagger definition from file
with open('swagger.xml', 'r') as file:
    swagger_content = file.read()

swagger_json = json.loads(swagger_content)

endpoint_dependencies = {}

for path, path_info in swagger_json['paths'].items():
    for method, method_info in path_info.items():
        endpoint = f"{method.upper()} {path}"
        dependencies = []

        # Check request body schema
        if 'requestBody' in method_info and 'content' in method_info['requestBody']:
            for content_type, content_info in method_info['requestBody']['content'].items():
                if 'schema' in content_info and '$ref' in content_info['schema']:
                    ref = content_info['schema']['$ref']
                    schema_name = ref.replace('#/components/schemas/', '')
                    schema = swagger_json['components']['schemas'][schema_name]
                    # Extract dependent parameters from schema properties
                    dependent_params = extract_dependent_params(schema)
                    dependencies.extend(dependent_params)

        # Check response schemas
        if 'responses' in method_info:
            for status, response_info in method_info['responses'].items():
                if 'content' in response_info:
                    for content_type, content_info in response_info['content'].items():
                        if 'schema' in content_info and '$ref' in content_info['schema']:
                            ref = content_info['schema']['$ref']
                            schema_name = ref.replace('#/components/schemas/', '')
                            schema = swagger_json['components']['schemas'][schema_name]
                            # Extract dependent parameters from schema properties
                            dependent_params = extract_dependent_params(schema)
                            dependencies.extend(dependent_params)

        if dependencies:
            endpoint_dependencies[endpoint] = dependencies

# Save the endpoint dependencies to a JSON file
with open('endpoint_dependencies.json', 'w') as file:
    json.dump(endpoint_dependencies, file, indent=2)