import json
import requests

# Read the Swagger definition from file
with open('swagger.xml', 'r') as file:
    swagger_content = file.read()

swagger_json = json.loads(swagger_content)

print("All endpoints:")
for path, path_info in swagger_json['paths'].items():
    for method in path_info:
        print(f"{method.upper()} {path}")

print("\nEndpoint dependencies:")
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
                    dependencies.append(schema_name)

        # Check response schemas
        if 'responses' in method_info:
            for status, response_info in method_info['responses'].items():
                if 'content' in response_info:
                    for content_type, content_info in response_info['content'].items():
                        if 'schema' in content_info and '$ref' in content_info['schema']:
                            ref = content_info['schema']['$ref']
                            schema_name = ref.replace('#/components/schemas/', '')
                            dependencies.append(schema_name)

        if dependencies:
            print(f"{endpoint} depends on:")
            for schema in dependencies:
                print(f"  - {schema}")
            print()

print("Example usage of GET /api-specs/{apiSpecId} endpoint:")
print('''
import requests

api_spec_id = "1234"
url = f"https://api.example.com/api-specs/{api_spec_id}"
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    api_spec = response.json()
    print("Fetched API spec:", api_spec)
    
    # The response contains an array of associatedResources
    associated_resources = api_spec['associatedResources']
    
    # and an array of publications
    publications = api_spec['publications']
    
    # which can be used for further API calls...
else:
    print("Error fetching API spec:", response.status_code, response.text)
'''.strip())