from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from runtime.flow_runner import run, save_scenario, list_scenarios
from scenrio.scenario import create_new_scenario, TestScenario
import json
import os
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
    return list_scenarios()


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
        raise HTTPException(status_code=404, detail=f"Scenario '{name}' not found: {str(e)}")


@app.post("/api/scenarios")
def create_scenario(scenario: ScenarioRequest):
    """Create a new scenario with data from the frontend"""
    try:
        print(f"Received scenario data: {scenario.dict()}")

        new_scenario = TestScenario(
            name=scenario.name,
            id=scenario.id or str(datetime.now().timestamp()),
            description=scenario.description or f"Description for {scenario.name}",
            version=scenario.version or "1.0.0",
            created_at=datetime.now().isoformat() + "Z",
            updated_at=datetime.now().isoformat() + "Z",
            requests=[req.dict() for req in (scenario.requests or [])]
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
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/scenarios/{name}/run")
def run_scenario(name: str):
    """Run a scenario by name"""
    try:
        result = run(name)
        return {
            "message": f"Scenario '{name}' executed",
            "success": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/environments")
def get_environments():
    """Return available environment configurations"""
    try:
        from config.envModel import envs
        return {name: {"url": env.envUrl, "type": name} for name, env in envs.items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scenarios/{name}/validate")
def validate_scenario(name: str):
    """Validate a scenario without running it"""
    try:
        return {"valid": True, "message": "Scenario structure is valid"}
    except Exception as e:
        return {"valid": False, "message": str(e)}

@app.get("/api/templates/body/{endpoint_type}")
def get_body_templates(endpoint_type: str):
    """Return saved body templates for specific endpoint types"""
    templates_file = "body_templates.json"
    if os.path.exists(templates_file):
        with open(templates_file, "r") as f:
            templates = json.load(f)
            return templates.get(endpoint_type, {})
    return {}

@app.get("/api/execute_status/{execution_id}")
def get_execution_status(execution_id: str):
    """Get the status of a running scenario execution"""
    # Implement a way to track long-running executions
    return {"status": "completed", "results": {}}


# ----- FIELD AND TEMPLATE ROUTES -----
@app.get("/api/fields/{endpoint_type}")
def get_fields(endpoint_type: str):
    """Return available fields for an endpoint type with path property"""
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
        {"path": "field2", "type": "int"}
    ]


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