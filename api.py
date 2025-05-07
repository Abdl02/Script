from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from runtime.flow_runner import run, save_scenario, list_scenarios
from scenrio.scenario import create_new_scenario, TestScenario
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


# ----- Pydantic models matching the frontend's expected structure -----
class Assertion(BaseModel):
    type: str
    value: str
    path: Optional[str] = None


class APIRequestModel(BaseModel):
    name: str
    method: str
    url: str
    headers: Dict[str, str] = {}
    body: Optional[Dict[str, Any]] = None
    save_as: Optional[str] = None
    assertions: List[Assertion] = []


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

# TODO: Need to list the request in the response, and correct res(TestScenario) [Abd]
@app.get("/api/scenarios/{name}")
def get_scenario(name: str):
    """Return full scenario details by name"""
    try:
        return {
            "name": name,
            "id": f"id_{name}",
            "description": f"Description for {name}",
            "version": "1.0.0",
            "created_at": datetime.now().isoformat() + "Z",
            "updated_at": datetime.now().isoformat() + "Z",
            "requests": []
        }
    except Exception as e:
        print(f"Error getting scenario {name}: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=404, detail=f"Scenario '{name}' not found: {str(e)}")


@app.post("/api/scenarios")
def create_scenario(scenario: ScenarioRequest):
    """Create a new scenario with data from the frontend"""
    try:
        print(f"Received scenario data: {scenario.dict()}")

        if not scenario.id:
            scenario.id = f"id_{scenario.name}_{datetime.now().timestamp()}"

        requests_data = []
        for req in (scenario.requests or []):
            req_dict = req.dict()
            assertions = []
            for assertion in req_dict.get("assertions", []):
                assertions.append(assertion)
            req_dict["assertions"] = assertions
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

        print(f"Created scenario object: {new_scenario.to_dict()}")

        # Save the scenario
        save_result = save_scenario(new_scenario)
        print(f"Save result: {save_result}")

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
        print(error_details)
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

#TODO new feature [ Mohammad, Abd]
@app.get("/api/templates/body/{endpoint_type}")
def get_body_templates(endpoint_type: str):
    """Return saved body templates for specific endpoint types"""
    try:
        templates_file = "body_templates.json"
        if os.path.exists(templates_file):
            with open(templates_file, "r") as f:
                templates = json.load(f)
                return templates.get(endpoint_type, {})
        return {}
    except Exception as e:
        print(f"Error getting body templates for {endpoint_type}: {str(e)}")
        return {}

#TODO Garbage, assertrion[delete]
@app.get("/api/execute_status/{execution_id}")
def get_execution_status(execution_id: str):
    """Get the status of a running scenario execution"""
    # Implement a way to track long-running executions
    return {"status": "completed", "results": {}}

# TODO add_field_from_path ,extract_fields_from_schema,fill_remaining_fields_with_random_data [Abd]
# ----- FIELD AND TEMPLATE ROUTES -----
@app.get("/api/fields/{endpoint_type}")
def get_fields(endpoint_type: str):
    """Return available fields for an endpoint type with path property"""
    print(f"Retrieving fields for endpoint type: {endpoint_type}")

    if endpoint_type == "api-specs":
        return [
            {"path": "name", "type": "string", "required": True},
            {"path": "description", "type": "string"},
            {"path": "contextPath", "type": "string"},
            {"path": "backendServiceUrl", "type": "string"},
            {"path": "status", "type": "string"},
            {"path": "type", "type": "string"},
            {"path": "style", "type": "string"},
            {"path": "authType", "type": "string"},
            {"path": "metaData.version", "type": "string"},
            {"path": "metaData.owner", "type": "string"},
            {"path": "metaData.category", "type": "string"},
            {"path": "metaData.tags", "type": "array"},
            {"path": "addVersionToContextPath", "type": "boolean"}
        ]

    return [
        {"path": "field1", "type": "string"},
        {"path": "field2", "type": "string"}
    ]

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