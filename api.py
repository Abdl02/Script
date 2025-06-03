from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from runtime.flow_runner import run, save_scenario, list_scenarios
from scenario.scenario import get_all_field_paths, TestScenario as TestScenarioModel  # Renamed to avoid conflict
from runtime.flow_runner import get_scenario_path, is_yaml_exists, yaml_file_to_object
from scenario.scenario import get_value_from_path
from difflib import get_close_matches
import json
import os
import traceback
import logging  # Import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- In-memory store for body templates (for demonstration) ---
# In a real application, this would be a database.
body_template_store: Dict[str, Dict[str, Any]] = {
    "api-specs": {
        "Basic API Spec": {
            "name": "sample-api-from-template",
            "description": "Sample API description from template",
            "contextPath": "/sample-api-template",
            "backendServiceUrl": "https://jsonplaceholder.typicode.com",
            "status": "DRAFT",
            "type": "PRIVATE",
            "style": "REST",
            "authType": "API_KEY",
            "metaData": {
                "version": "1.0.0",
                "owner": "template-owner",
                "category": "Template Category",
                "tags": ["template", "api", "example"]
            },
            "addVersionToContextPath": True
        }
    },
    "products": {
        "Standard Product": {
            "name": "standard-product-template",
            "desc": "A standard product from a template",
            "version": "1.0.0",
            "apiSpecs": [],
            "segment": "General",
            "premium": False,
            "status": "DRAFT"
        }
    }
    # Add more endpoint types and their templates as needed
}
# --- End of in-memory store ---

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
    # Add assertions if they are part of the request model sent from frontend
    assertions: Optional[List[Dict[str, Any]]] = None
    save_as: Optional[str] = None


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
    logger.info("Received request for /api/scenarios")
    try:
        scenarios = list_scenarios()
        logger.info(f"Returning {len(scenarios)} scenarios: {scenarios}")
        return scenarios
    except Exception as e:
        logger.error(f"Error retrieving scenarios: {str(e)}\n{traceback.format_exc()}")
        return []


@app.get("/api/scenarios/{name}")
def get_scenario(name: str):
    """Return full scenario details by name"""
    logger.info(f"Received request for /api/scenarios/{name}")
    try:
        path = get_scenario_path(name)

        if not is_yaml_exists(path):
            logger.warning(f"Scenario '{name}' not found at path: {path}")
            raise HTTPException(status_code=404, detail=f"Scenario '{name}' not found")

        scenario_obj = yaml_file_to_object(path, TestScenarioModel)  # Use aliased TestScenarioModel
        # Ensure to_dict method exists and is called correctly
        if hasattr(scenario_obj, 'to_dict') and callable(getattr(scenario_obj, 'to_dict')):
            scenario_dict = scenario_obj.to_dict()
            logger.info(f"Successfully retrieved and converted scenario '{name}' to dict.")
            return scenario_dict
        else:
            logger.error(f"Scenario object for '{name}' does not have a to_dict method.")
            # Fallback or error, depending on how TestScenarioModel is structured
            # If TestScenarioModel is a Pydantic model, .dict() or .model_dump() might be available
            if hasattr(scenario_obj, 'model_dump'):  # Pydantic v2
                scenario_dict = scenario_obj.model_dump(mode='json')  # or mode='python'
                logger.info(f"Successfully retrieved and converted Pydantic scenario '{name}' using model_dump.")
                return scenario_dict
            elif hasattr(scenario_obj, 'dict'):  # Pydantic v1
                scenario_dict = scenario_obj.dict()
                logger.info(f"Successfully retrieved and converted Pydantic scenario '{name}' using dict.")
                return scenario_dict
            raise HTTPException(status_code=500, detail="Scenario object cannot be serialized.")

    except FileNotFoundError:  # More specific exception
        logger.warning(f"Scenario file for '{name}' not found.")
        raise HTTPException(status_code=404, detail=f"Scenario '{name}' not found.")
    except Exception as e:
        logger.error(f"Error getting scenario {name}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error retrieving scenario '{name}': {str(e)}")


@app.post("/api/scenarios")
def create_scenario(scenario: ScenarioRequest):
    """Create a new scenario with data from the frontend"""
    logger.info(f"Received request to create scenario: {scenario.name}")
    try:
        if not scenario.id:
            scenario.id = f"id_{scenario.name.replace(' ', '_')}_{int(datetime.now().timestamp())}"

        requests_data = []
        if scenario.requests:
            for req_model in scenario.requests:
                req_dict = req_model.model_dump(exclude_none=True)  # Use model_dump for Pydantic
                requests_data.append(req_dict)

        logger.debug(f"Processed requests data: {requests_data}")

        new_scenario_obj = TestScenarioModel(  # Use aliased TestScenarioModel
            name=scenario.name,
            id=scenario.id,
            description=scenario.description or f"Description for {scenario.name}",
            version=scenario.version or "1.0.0",
            created_at=scenario.created_at or datetime.now().isoformat() + "Z",
            updated_at=scenario.updated_at or datetime.now().isoformat() + "Z",
            requests=requests_data  # This should be a list of dicts
        )
        logger.debug(f"TestScenarioModel object created: {new_scenario_obj}")

        save_result = save_scenario(new_scenario_obj)  # Pass the object
        logger.info(f"Scenario '{scenario.name}' saved with result: {save_result}")
        return {
            "message": f"Scenario '{scenario.name}' created successfully.",
            "success": save_result,
            "scenario": {
                "name": new_scenario_obj.name,
                "id": new_scenario_obj.id
            }
        }
    except Exception as e:
        error_details = f"Error creating scenario: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_details)
        raise HTTPException(status_code=400, detail=error_details)


@app.post("/api/scenarios/{name}/run")
def run_scenario_endpoint(name: str, body: dict = Body(...)):  # Renamed from run to avoid conflict
    """Run a scenario by name and return the result"""
    logger.info(f"Received request to run scenario: {name} with body: {body}")
    try:
        environment = body.get("environment", "localDev")
        if not environment:
            logger.warning("Environment not provided in run request, defaulting to 'localDev'.")
            environment = "localDev"

        result = run(name, environment)  # Call the original run function
        logger.info(f"Scenario '{name}' executed with result: {result}")
        return result
    except Exception as e:
        error_details = f"Error running scenario '{name}': {str(e)}\n{traceback.format_exc()}"
        logger.error(error_details)
        raise HTTPException(status_code=400, detail=error_details)


@app.get("/api/environments")
def get_environments():
    """Return available environment configurations"""
    logger.info("Received request for /api/environments")
    try:
        from config.envModel import envs  # Local import to ensure it's fresh if modified
        if not envs or not isinstance(envs, dict):
            logger.error("Environments data is not loaded correctly or is not a dictionary.")
            # Fallback to default if envs is not as expected
            return {
                "localDev": {"url": "http://localhost:8099", "type": "localDev"},
                "dev": {"url": "https://dev.example.com", "type": "dev"}
            }

        formatted_envs = {name: {"url": env.envUrl, "type": name} for name, env in envs.items() if
                          hasattr(env, 'envUrl')}
        logger.info(f"Returning environments: {formatted_envs}")
        return formatted_envs
    except ImportError:
        logger.error("Failed to import envModel or envs.")
        return {"localDev": {"url": "http://localhost:8099", "type": "localDev"}}  # Fallback
    except Exception as e:
        logger.error(f"Error getting environments: {str(e)}\n{traceback.format_exc()}")
        # Return default environments instead of failing
        return {
            "localDev": {"url": "http://localhost:8099", "type": "localDev"},
            "dev": {"url": "https://dev.example.com", "type": "dev"}
        }


# ----- FIELD AND TEMPLATE ROUTES -----
@app.get("/item/fields/{endpoint_type}")
def get_fields(endpoint_type: str):
    """Return available fields for an endpoint type with path property using validator"""
    logger.info(f"Received request for fields of endpoint_type: {endpoint_type}")
    from validation.endpoint_validations import ValidatorFactory  # Local import

    # Normalize endpoint_type for matching (e.g., handle potential slashes)
    normalized_endpoint_type = endpoint_type.split("/")[0].lower()
    logger.debug(f"Normalized endpoint_type for validator lookup: {normalized_endpoint_type}")

    validator_class = ValidatorFactory.get_validator(normalized_endpoint_type)

    if not validator_class:
        closest_match_key = get_close_matches(normalized_endpoint_type, ValidatorFactory.get_all_validator_names(), n=1,
                                              cutoff=0.6)
        if closest_match_key:
            logger.warning(
                f"No exact validator for '{normalized_endpoint_type}', using closest match: '{closest_match_key[0]}'")
            validator_class = ValidatorFactory.get_validator(closest_match_key[0])
        else:
            logger.warning(
                f"No validator or close match found for endpoint_type: {normalized_endpoint_type}. Returning empty list.")
            return []

    if not hasattr(validator_class, 'get_valid_body'):
        logger.warning(
            f"Validator for '{normalized_endpoint_type}' does not have 'get_valid_body' method. Returning empty list.")
        return []

    try:
        sample_body = validator_class.get_valid_body()
        logger.debug(f"Sample body for '{normalized_endpoint_type}': {sample_body}")

        fields_with_paths = get_all_field_paths(sample_body)
        logger.debug(f"Extracted field paths: {fields_with_paths}")

        result = []
        for field_path in fields_with_paths:
            field_value = get_value_from_path(sample_body, field_path)
            field_type = "string"  # Default

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

            # Basic heuristic for required fields
            required = "name" in field_path.lower() or field_path.lower().endswith(".id")

            result.append({
                "path": field_path,
                "type": field_type,
                "required": required
            })
        logger.info(f"Returning {len(result)} fields for endpoint_type: {endpoint_type}")
        return result
    except Exception as e:
        logger.error(f"Error processing fields for '{normalized_endpoint_type}': {str(e)}\n{traceback.format_exc()}")
        return []


@app.post("/item/fields/{endpoint_type}")
def fetch_body_fields(endpoint_type: str, body: Dict[str, Any] = Body(default_factory=dict)):
    """
    Fetch and analyze fields for a specific endpoint type from its URL or provided body.
    This endpoint is used when the user clicks the "Fetch" button next to the URL field
    or to get a schema based on a potentially partial body.
    """
    logger.info(f"Received POST request for fields of endpoint_type: {endpoint_type} with body: {body}")
    from validation.endpoint_validations import ValidatorFactory  # Local import

    normalized_endpoint_type = endpoint_type.split("/")[0].lower()
    logger.debug(f"Normalized endpoint_type for validator lookup: {normalized_endpoint_type}")

    validator_class = ValidatorFactory.get_validator(normalized_endpoint_type)

    if not validator_class or not hasattr(validator_class, 'get_valid_body'):
        logger.warning(f"No validator with 'get_valid_body' for endpoint_type: {normalized_endpoint_type}")
        # Fallback: try to infer schema from the provided body if any
        if body:
            logger.info("Attempting to infer schema from provided body as validator is missing.")
            fields_from_body = get_all_field_paths(body)
            result = []
            for field_path in fields_from_body:
                field_value = get_value_from_path(body, field_path)
                field_type = "string"
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
                result.append({"path": field_path, "type": field_type,
                               "required": False})  # Cannot infer required from body alone
            return {"fields": result, "message": "Inferred fields from provided body due to missing validator."}
        return {"fields": [], "message": f"No validator found for endpoint type: {endpoint_type}"}

    try:
        sample_body = validator_class.get_valid_body()
        logger.debug(f"Sample body for '{normalized_endpoint_type}': {sample_body}")

        # If a user provides a body, we can try to merge or prioritize its structure,
        # but for now, we'll primarily rely on the validator's sample body.
        # Future enhancement: merge `body` with `sample_body` intelligently.

        fields_with_paths = get_all_field_paths(sample_body)
        logger.debug(f"Extracted field paths from sample_body: {fields_with_paths}")

        result = []
        for field_path in fields_with_paths:
            field_value = get_value_from_path(sample_body, field_path)
            field_type = "string"
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

            required = "name" in field_path.lower() or field_path.lower().endswith(".id")

            result.append({
                "path": field_path,
                "type": field_type,
                "required": required
            })
        logger.info(f"Successfully retrieved {len(result)} fields for endpoint_type: {endpoint_type}")
        return {"fields": result, "message": "Successfully retrieved fields based on validator."}
    except Exception as e:
        logger.error(f"Error fetching fields for '{normalized_endpoint_type}': {str(e)}\n{traceback.format_exc()}")
        return {"fields": [], "message": f"Error fetching fields: {str(e)}"}


@app.get("/api/templates/body/{endpoint_type}")
def get_body_templates(endpoint_type: str):
    """Return body templates for the specified endpoint type."""
    logger.info(f"Request for body templates for endpoint_type: {endpoint_type}")
    normalized_type = endpoint_type.lower()
    templates = body_template_store.get(normalized_type, {})

    # If no specific templates, try to generate one from validator
    if not templates:
        logger.info(f"No stored templates for '{normalized_type}', attempting to generate from validator.")
        from validation.endpoint_validations import ValidatorFactory  # Local import
        validator_class = ValidatorFactory.get_validator(normalized_type)
        if validator_class and hasattr(validator_class, 'get_valid_body'):
            try:
                generated_template_body = validator_class.get_valid_body()
                template_name = f"Default {normalized_type.capitalize()} Template"
                templates = {template_name: generated_template_body}
                logger.info(f"Generated default template for '{normalized_type}'.")
            except Exception as e:
                logger.error(f"Error generating default template for '{normalized_type}': {str(e)}")
        else:
            logger.warning(
                f"No validator or get_valid_body method for '{normalized_type}' to generate default template.")

    logger.info(f"Returning {len(templates)} templates for '{normalized_type}'.")
    return templates


@app.post("/api/templates/body/{endpoint_type}")
def save_body_template(endpoint_type: str, name: str = Body(...), body: Dict[str, Any] = Body(...)):
    """Save a new body template (in-memory for now)."""
    logger.info(f"Request to save body template '{name}' for endpoint_type: {endpoint_type}")
    normalized_type = endpoint_type.lower()
    if normalized_type not in body_template_store:
        body_template_store[normalized_type] = {}

    if name in body_template_store[normalized_type]:
        logger.warning(f"Template '{name}' for '{normalized_type}' already exists. Overwriting.")

    body_template_store[normalized_type][name] = body
    logger.info(f"Template '{name}' for '{normalized_type}' saved successfully.")
    return {"message": f"Template '{name}' saved for endpoint type '{endpoint_type}'.", "template_name": name}


@app.get("/api/urls")
def get_urls(chars: Optional[str] = None):
    """Return a list of URLs (endpoint names from validators) based on the provided characters"""
    logger.info(f"Request for URLs, chars: {chars}")
    from validation.endpoint_validations import ValidatorFactory  # Local import

    all_validator_names = ValidatorFactory.get_all_validator_names()
    # Typically, URLs are more complex. For this system, "URLs" seem to map to endpoint types/paths.
    # We can use validator names as a proxy for available "base paths" or "endpoint types".
    urls = [f"/{name}" for name in all_validator_names]  # Prefix with / to make them look like paths

    if chars:
        urls = [url for url in urls if chars.lower() in url.lower()]
    logger.info(f"Returning {len(urls)} URL suggestions.")
    return urls


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server with Uvicorn.")
    # Ensure SCENARIO_SAVE_DIR is set or has a default for flow_runner
    os.environ.setdefault("SCENARIO_SAVE_DIR", "./scenarios")
    uvicorn.run(app, host="0.0.0.0", port=8000)