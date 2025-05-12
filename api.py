from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from runtime.flow_runner import run, save_scenario, list_scenarios
from scenario.scenario import get_all_field_paths
from runtime.flow_runner import get_scenario_path, is_yaml_exists, yaml_file_to_object
from scenario.scenario import get_value_from_path
from difflib import get_close_matches
from scenario.scenario import TestScenario
import json
import os
import traceback
from validation.endpoint_validations import ValidatorFactory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class APIRequestModel(BaseModel):
    name: str
    method: str
    url: str
    headers: Dict[str, str] = {}
    body: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None

class ScenarioRequest(BaseModel):
    name: str
    id: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    requests: Optional[List[APIRequestModel]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# ----- SCENARIO ROUTES -----
@app.get("/api/scenarios")
def get_scenarios():
    """Return list of scenario names as strings to match frontend expectations"""
    try:
        scenarios = list_scenarios()
        print(f"Retrieved scenarios: {scenarios}")
        return scenarios
    except Exception as e:
        print(f"Error retrieving scenarios: {str(e)}")
        print(traceback.format_exc())
        return []

# TODO: Need to list the request in the response, and correct res(TestScenario) instead string with all fields [just the request] [Abd]
@app.get("/api/scenarios/{name}")
def get_scenario(name: str):
    """Return full scenario details by name"""
    try:
        path = get_scenario_path(name)

        if not is_yaml_exists(path):
            raise HTTPException(status_code=404, detail=f"Scenario '{name}' not found")

        scenario = yaml_file_to_object(path, TestScenario)
        scenario_dict = scenario.to_dict()

        return scenario_dict

    except Exception as e:
        print(f"Error getting scenario {name}: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=404, detail=f"Scenario '{name}' not found: {str(e)}")

@app.post("/api/scenarios")
def create_scenario(scenario: ScenarioRequest):
    """Create a new scenario with data from the frontend"""
    try:
        if not scenario.id:
            scenario.id = f"id_{scenario.name}_{datetime.now().timestamp()}"

        requests_data = []
        for req in (scenario.requests or []):
            req_dict = req.dict()
            requests_data.append(req_dict)

        new_scenario = TestScenario(
            name=scenario.name,
            id=scenario.id,
            description=scenario.description or f"Description for {scenario.name}",
            version=scenario.version or "1.0.0",
            created_at=scenario.created_at or datetime.now().isoformat() + "Z",
            updated_at=scenario.updated_at or datetime.now().isoformat() + "Z",
            requests=requests_data
        )

        # Save the scenario
        save_result = save_scenario(new_scenario)
        return {
            "message": f"Scenario '{scenario.name}' created",
            "success": save_result,
            "scenario": {
                "name": new_scenario.name,
                "id": new_scenario.id
            }
        }
    except Exception as e:
        error_details = f"Error creating scenario: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=400, detail=error_details)


@app.post("/api/scenarios/{name}/run")
def run_scenario(name: str, body: dict = Body(...)):
    """Run a scenario by name and return the result"""
    try:
        environment = body.get("environment", "localDev")
        print(f"Running scenario: {name} with environment: {environment}")
        return run(name, environment)
    except Exception as e:
        error_details = f"Error running scenario '{name}': {str(e)}"
        print(error_details)
        raise HTTPException(status_code=400, detail=error_details)

@app.get("/api/environments")
def get_environments():
    """Return available environment configurations"""
    try:
        from config.envModel import envs
        return {name: {"url": env.envUrl, "type": name} for name, env in envs.items()}
    except Exception as e:
        print(f"Error getting environments: {str(e)}")
        print(traceback.format_exc())
        # Return default environments instead of failing
        return {
            "localDev": {"url": "http://localhost:8099", "type": "localDev"},
            "dev": {"url": "https://dev.example.com", "type": "dev"}
        }

# TODO add_field_from_path ,extract_fields_from_schema,fill_remaining_fields_with_random_data [Abd] handle get field according to get_validator that in endpoint_validations.py and fill them randomly if not filled as in enhanced_body_creation in scenario.py
# ----- FIELD AND TEMPLATE ROUTES -----
@app.get("/item/fields/{endpoint_type}")
def get_fields(endpoint_type: str):
    """Return available fields for an endpoint type with path property using validator"""
    print(f"Retrieving fields for endpoint type: {endpoint_type}")

    splited = endpoint_type.split("/")
    all_validators = ValidatorFactory.validators
    validator = all_validators.get(splited[0])

    # if it was not found, find the most similar one
    if not validator:
        closest_match = get_close_matches(splited[0], all_validators, n=1)
        if closest_match:
            validator = ValidatorFactory.validators.get(closest_match[0])

    if validator and hasattr(validator, 'get_valid_body'):
        sample_body = validator.get_valid_body()
        fields = get_all_field_paths(sample_body)
        result = []
        for field_path in fields:
            field_type = "string"

            field_value = get_value_from_path(sample_body, field_path)
            if isinstance(field_value, bool):
                field_type = "boolean"
            elif isinstance(field_value, int):
                field_type = "integer"
            elif isinstance(field_value, float):
                field_type = "number"
            elif isinstance(field_value, list):
                field_type = "array"
            elif isinstance(field_value, dict):
                field_type = "object"

            required = field_path == "name" or field_path.endswith(".name")

            result.append({
                "path": field_path,
                "type": field_type,
                "required": required
            })

        return result

    return []

# fetch when button next to url* ae pressed
@app.post("/item/fields/{endpoint_type}")
def fetch_body_fields(endpoint_type: str, body: Dict[str, Any] = Body(default=None)):
    """
    Fetch and analyze fields for a specific endpoint type from its URL

    This endpoint is used when the user clicks the "Fetch" button next to the URL field
    to dynamically extract fields based on the URL pattern.
    """
    try:
        print(f"Fetching fields for endpoint type: {endpoint_type}")
        url = body.get("url") if body else None

        from validation.endpoint_validations import ValidatorFactory
        from scenario.scenario import get_all_field_paths, get_value_from_path

        validator = ValidatorFactory.get_validator(endpoint_type)

        if not validator or not hasattr(validator, 'get_valid_body'):
            return {"fields": [], "message": f"No validator found for endpoint type: {endpoint_type}"}

        sample_body = validator.get_valid_body()

        fields = get_all_field_paths(sample_body)

        result = []
        for field_path in fields:
            field_type = "string"  # Default type

            field_value = get_value_from_path(sample_body, field_path)
            if isinstance(field_value, bool):
                field_type = "boolean"
            elif isinstance(field_value, int):
                field_type = "integer"
            elif isinstance(field_value, float):
                field_type = "number"
            elif isinstance(field_value, list):
                field_type = "array"
            elif isinstance(field_value, dict):
                field_type = "object"

            required = field_path == "name" or field_path.endswith(".name")

            result.append({
                "path": field_path,
                "type": field_type,
                "required": required
            })

        return {"fields": result, "message": "Successfully retrieved fields"}
    except Exception as e:
        print(f"Error fetching fields: {str(e)}")
        print(traceback.format_exc())
        return {"fields": [], "message": f"Error fetching fields: {str(e)}"}

#TODO: handle all endpoints body fields types,new feature [zaro,Abd]
@app.get("/api/templates/{endpoint_type}")
def get_templates(endpoint_type: str):
    """Return templates for the specified endpoint type"""
    if endpoint_type == "api-specs":
        return [
            {
                "name": "Basic API Spec",
                "template": {
                    "name": "sample-api",
                    "description": "Sample API description",
                    "contextPath": "/sample-api",
                    "backendServiceUrl": "https://jsonplaceholder.typicode.com",
                    "status": "DRAFT",
                    "type": "PRIVATE",
                    "style": "REST",
                    "authType": "API_KEY",
                    "metaData": {
                        "version": "1.0.0",
                        "owner": "sample-owner",
                        "category": "Sample Category",
                        "tags": ["sample", "api", "test"]
                    },
                    "addVersionToContextPath": True
                }
            }
        ]
    return [
        {"template": f"Template for {endpoint_type}", "example": {"key": "value"}}
    ]

@app.get("/api/urls")
def get_urls(chars: Optional[str] = None):
    """Return a list of URLs based on the provided characters"""
    # Implement logic to fetch URLs based on the provided characters
    urls = ValidatorFactory.get_all_validator_names()
    if chars:
        urls = [url for url in urls if chars in url]
    return urls

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)