"""
Endpoint validation rules based on ModelFactory
"""
import uuid
import random
import string
from enum import Enum
from typing import Dict, List, Any, Optional
# from datetime import datetime, timedelta # Not currently used, can be removed if not needed


# Enums from your model
class ApiType(Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    PARTNER = "PARTNER"


class ApiStyle(Enum):
    REST = "REST"
    SOAP = "SOAP"
    WEB_SOCKET = "WEB_SOCKET"
    GRPC = "GRPC"


class AuthenticatorType(Enum):
    BASIC = "BASIC"
    OAUTH = "OAUTH"
    API_KEY = "API_KEY"
    KEYLESS = "KEYLESS" # Added based on usage


class EnvironmentType(Enum):
    DEV = "DEV"
    TEST = "TEST" # Added based on usage
    STG = "STG"
    SDB = "SDB"
    PRD = "PRD"


class ConsumerStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"
    DRAFT = "DRAFT" # Added based on usage


class ContactType(Enum):
    BUSINESS = "BUSINESS"
    TECHNICAL = "TECHNICAL"
    ADMINISTRATIVE = "ADMINISTRATIVE"


def manipulate_and_create_random_data(body: Any, apiPath: str) -> Any:
    """
    Manipulates the provided request body by filling in missing fields with
    random valid data based on the endpoint type derived from apiPath.

    Args:
        body (Any): The user-provided request body. Can be a dict or a list of dicts.
                    If None, a full random body will be generated.
        apiPath (str): The API path/URL, used to determine the endpoint type and
                       fetch the appropriate validator.

    Returns:
        Any: The manipulated body with missing fields filled, or a fully generated
             random body if the input `body` was None.

    Raises:
        ValueError: If no suitable validator is found for the given apiPath.
        TypeError: If the input body type is incompatible with the validator's output type
                   (e.g., list expected but dict provided by validator for list items).
    """
    if body is None: # If no body is provided, generate a full random one
        body = {} # Initialize as dict, validator might return list or dict

    # Determine the endpoint key from the apiPath
    # Example: "http://localhost:8099/api/v1/api-specs" -> "api-specs"
    # Example: "/consumers" -> "consumers"
    if isinstance(apiPath, str):
        path_segments = apiPath.strip("/").split("/")
        # Try to find a known validator key by looking from the end of the path
        # This handles cases like /api/v1/endpoint_key or /endpoint_key
        api_key_for_validator = None
        for i in range(len(path_segments) -1, -1, -1):
            potential_key = path_segments[i].lower()
            if ValidatorFactory.get_validator(potential_key):
                api_key_for_validator = potential_key
                break
        if not api_key_for_validator and path_segments: # Fallback to last segment if specific not found
            api_key_for_validator = path_segments[-1].lower()
        elif not path_segments: # Handle empty or root path
            api_key_for_validator = "default" # Or some other default key
    else:
        raise ValueError("apiPath must be a string.")

    validator = ValidatorFactory.get_validator(api_key_for_validator)

    if not validator or not hasattr(validator, 'get_valid_body'):
        # If no specific validator, it's hard to guess, so return body as is or raise error
        # For now, let's log a warning and return the body as is, or an empty dict if body was None.
        # print(f"Warning: No valid validator found for apiPath: {apiPath} (derived key: {api_key_for_validator}). Returning body as is or empty.")
        return body if body is not None else {}


    # Generate a sample valid body structure using the validator
    random_data_template = validator.get_valid_body()

    # Helper function to recursively merge/fill data
    def fill_missing_fields(target_data, template_data):
        if isinstance(template_data, dict):
            if not isinstance(target_data, dict):
                # If target is not a dict (e.g. None or wrong type), replace it with a copy of template
                return template_data.copy() if template_data is not None else {}

            # Iterate over template keys to ensure all fields from template are considered
            for key, template_value in template_data.items():
                if key not in target_data or target_data[key] is None:
                    # If key is missing in target or its value is None, use template's value
                    target_data[key] = template_value # This could be a primitive or a nested structure
                elif isinstance(template_value, dict):
                    # If value is a dict, recurse
                    target_data[key] = fill_missing_fields(target_data.get(key, {}), template_value)
                elif isinstance(template_value, list) and isinstance(target_data.get(key), list):
                    # If both are lists, try to fill items (basic for now, could be more complex)
                    # This part might need more sophisticated list merging logic if item structures vary
                    target_list = target_data[key]
                    template_list = template_value
                    for i in range(len(template_list)):
                        if i < len(target_list):
                            if isinstance(target_list[i], dict) and isinstance(template_list[i], dict):
                                target_list[i] = fill_missing_fields(target_list[i], template_list[i])
                            # Add more conditions if lists can contain non-dict items that need merging
                        else:
                            # If target list is shorter, append template items (or copies)
                            # target_list.append(template_list[i]) # This might share refs if template_list[i] is mutable
                            pass # For now, don't extend lists if target is shorter to avoid unexpected additions
                # If target_data[key] exists and is not None, and not a dict/list to recurse, keep target's value
            return target_data
        elif isinstance(template_data, list):
             # If template is a list, and target is not, replace target with a copy of template
            if not isinstance(target_data, list):
                return [item.copy() if isinstance(item, dict) else item for item in template_data] if template_data is not None else []

            # If both are lists, process each item
            # This assumes target_data should have items corresponding to random_data_template items
            processed_list = []
            for i in range(len(target_data)): # Iterate over the user's provided list items
                if i < len(template_data): # If there's a corresponding template item
                    processed_list.append(fill_missing_fields(target_data[i], template_data[i]))
                else: # If user's list is longer than template, keep user's extra items
                    processed_list.append(target_data[i])

            # If template list is longer, one might decide to append missing items
            # For now, we only process up to the length of the target_data to avoid adding unexpected items
            # if len(template_data) > len(target_data):
            #    for i in range(len(target_data), len(template_data)):
            #        processed_list.append(template_data[i]) # Or a copy

            return processed_list
        return target_data # Primitives or types not handled are returned as is

    # Start the filling process
    manipulated_body = fill_missing_fields(body if body is not None else {}, random_data_template)

    return manipulated_body


class EndpointValidations:
    DEFAULT_BACKEND_SERVICE_URL = "https://jsonplaceholder.typicode.com"
    DEV_GATEWAY_ENVIRONMENT_ID = "apigw-local01-23122023" # Example ID
    STG_GATEWAY_ENVIRONMENT_ID = "apigw-stg01-example"
    SDB_GATEWAY_ENVIRONMENT_ID = "apigw-sdb01-example"
    VALID_TEST_GW_ENV_URL = "https://gw01.test.dgate.digitinary.net" # Example URL
    DELETED_API_GATEWAY_ENVIRONMENT_ID = "deleted-env-example"
    PUBLICATION_FLOW_ID = 1000 # Example ID

    @staticmethod
    def generate_random_string(length: int = 12, prefix: str = "") -> str:
        random_part = str(uuid.uuid4()).replace("-", "")[:length - len(prefix)]
        return f"{prefix}{random_part}"

    @staticmethod
    def generate_random_email() -> str:
        return f"user_{EndpointValidations.generate_random_string(5)}@example.com"

    @staticmethod
    def generate_valid_phone() -> str:
        return f"+1{random.randint(200, 999)}{random.randint(1000000, 9999999)}"

    @staticmethod
    def generate_valid_version() -> str:
        return f"{random.randint(0,9)}.{random.randint(0,9)}.{random.randint(0,9)}"


class ApiSpecValidations:
    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        name = EndpointValidations.generate_random_string(prefix="api_")
        return {
            "name": name,
            "description": f"Description for {name}",
            "contextPath": f"/{name.replace('_', '-')}/v{random.randint(1,3)}",
            "backendServiceUrl": EndpointValidations.DEFAULT_BACKEND_SERVICE_URL, # Corrected variable name
            "status": "DRAFT",
            "type": random.choice(list(ApiType)).value,
            "style": random.choice(list(ApiStyle)).value,
            "authType": random.choice(list(AuthenticatorType)).value,
            "metaData": {
                "version": EndpointValidations.generate_valid_version(),
                "owner": EndpointValidations.generate_random_string(prefix="owner_"),
                "category": "General",
                "tags": [f"tag{i}" for i in range(random.randint(1,3))]
            },
            "addVersionToContextPath": random.choice([True, False]),
            "predicates": [],
            "requestPolicies": [],
            "responsePolicies": []
        }
    # ... (keep invalid bodies if needed for other tests)

class EnvironmentModelValidations:
    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        env_type = random.choice(list(EnvironmentType)).value
        return {
            "name": f"Env_{env_type}_{EndpointValidations.generate_random_string(5)}",
            "url": f"https://gw.{env_type.lower()}.example.com",
            "backendServiceUrls": [EndpointValidations.DEFAULT_BACKEND_SERVICE_URL, f"https://service2.{env_type.lower()}.example.com"],
            "type": env_type,
            "status": "ACTIVE", # Added status
            "authServerUrl": f"https://keycloak.{env_type.lower()}.example.com/auth", # Added
            "authServerName": f"{env_type.lower()}-realm", # Added
            "clientId": EndpointValidations.generate_random_string(10), # Added
            "clientSecret": EndpointValidations.generate_random_string(20) # Added
        }
    # ...

class CredentialModelValidations:
    @staticmethod
    def get_valid_body() -> List[Dict[str, Any]]: # Changed to list as per API expectation
        auth_type = random.choice(list(AuthenticatorType)).value
        credential: Dict[str, Any] = {"authenticatorType": auth_type}
        if auth_type == AuthenticatorType.BASIC.value:
            credential["username"] = EndpointValidations.generate_random_string(prefix="user_")
            credential["password"] = EndpointValidations.generate_random_string(12)
        elif auth_type == AuthenticatorType.OAUTH.value:
            credential["clientId"] = EndpointValidations.generate_random_string(prefix="oauth_client_")
            credential["clientSecret"] = EndpointValidations.generate_random_string(24)
            credential["clientName"] = EndpointValidations.generate_random_string(prefix="OAuthApp_")
            credential["redirectUrls"] = [f"https://app.example.com/callback{i}" for i in range(random.randint(1,2))]
        elif auth_type == AuthenticatorType.API_KEY.value:
            credential["apiKeyClientName"] = EndpointValidations.generate_random_string(prefix="apikey_app_")
            # apiKeyClientToken is often generated by the server, so not included here
            # Or if it needs to be sent:
            # credential["apiKeyClientToken"] = EndpointValidations.generate_random_string(32)
        # KEYLESS has no specific credential fields to add here
        return [credential] # API expects a list of credentials
    # ...

class AuthenticatorModelValidations:
    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        auth_type = random.choice(list(AuthenticatorType)).value
        body = {
            "name": f"{auth_type}_Auth_{EndpointValidations.generate_random_string(4)}",
            "type": auth_type,
            "status": "PENDING", # Default status
            "defaultAuth": random.choice([True, False]),
        }
        if auth_type == AuthenticatorType.OAUTH.value:
            body["tokenIssuerUrl"] = f"https://keycloak.example.com/auth/realms/{EndpointValidations.generate_random_string(5)}"
        # "environmentModel" and "credentials" are often linked/set separately or are more complex
        return body
    # ...

class ApiPolicyValidations: # Renamed from Policy to avoid conflict
    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        return ApiPolicyValidations.get_valid_request_rate_limiter_policy()

    @staticmethod
    def get_valid_request_rate_limiter_policy() -> Dict[str, Any]:
        return {
            "policyName": "REQUEST_RATE_LIMITER", # This should match an enum if available
            "httpExchange": "REQUEST",
            "order": random.randint(1, 10),
            "args": {
                "PER_SECONDS": str(random.randint(1, 60)),
                "NO_OF_REQUESTS": str(random.randint(5, 100))
            }
        }
    # ... (add other policy types)

class ConsumerModelValidations:
    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        name = EndpointValidations.generate_random_string(prefix="Consumer_")
        return {
            "consumerKey": name.lower().replace("_", "-"), # Derived from name
            "name": name,
            "consumerType": "GENERAL", # Default or random from an enum
            "segment": "B2B", # Default or random
            "status": random.choice(list(ConsumerStatus)).value,
            "source": "MANUAL", # Default or random
            "description": f"Test consumer: {name}",
            "logo": "https://example.com/logo.png",
            "organization": {
                "companyRegistrationNo": EndpointValidations.generate_random_string(10, prefix="REG"),
                "legalEntityIdentification": EndpointValidations.generate_random_string(10, prefix="LEI"),
                "businessName": f"{name} Ltd.",
                "legalEntityName": f"{name} Holdings",
                "country": "US"
            },
            "contacts": [{
                "contactType": random.choice(list(ContactType)).value,
                "firstName": "Tech",
                "lastName": "Support",
                "jobTitle": "Support Lead",
                "email": EndpointValidations.generate_random_email(),
                "mobileNo": EndpointValidations.generate_valid_phone(),
                "countryCode": "+1"
            }],
            # "projects" and "users" are often created/linked in separate steps
        }
    # ...

class ProductModelValidations:
    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        name = EndpointValidations.generate_random_string(prefix="Product_")
        return {
            "name": name,
            "desc": f"Description for {name}",
            "status": "DRAFT",
            "segment": "Enterprise",
            "version": EndpointValidations.generate_valid_version(),
            "premium": random.choice([True, False]),
            "availableOnDevPortal": random.choice([True, False]),
            "apiSpecs": [], # Typically linked via IDs after creation
            # "productPlanPrices": [] # Also often linked
        }
    # ...

class PlanModelValidations:
    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        name = EndpointValidations.generate_random_string(prefix="Plan_")
        return {
            "name": name,
            "desc": f"Description for {name}",
            "definitionType": "STANDARD", # Or random from enum
            "priceType": "USAGE_BASED_CHARGES", # Or random
            "planStatus": "DRAFT", # Or random
            "renewalTypeOptions": ["AUTO", "MANUAL"],
            "subscriptionPeriodOptions": ["MONTHLY", "YEARLY"],
            "premium": random.choice([True, False]),
            # "productPlanPrices": [] # Often linked
        }
    # ...

class SubscriptionModelValidations:
    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        # This often depends on existing consumer, project, and plan IDs.
        # For a generic template:
        return {
            "projectId": 1, # Placeholder, should be a valid existing project ID
            "planId": 1, # Placeholder, should be a valid existing plan ID
            "renewalType": "AUTO",
            "subscriptionPeriod": "MONTHLY",
            "trial": False,
            "status": "PENDING", # Initial status
            # "runtimeConfigPublicationModel": { ... } # This is complex and context-dependent
        }
    # ...

# Add other validation classes as needed, following the pattern...
class GlobalPolicyValidations:
    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        return GlobalPolicyValidations.get_valid_ip_filtration_policy()

    @staticmethod
    def get_valid_ip_filtration_policy() -> Dict[str, Any]:
        return {
            "globalPolicyName": "IP_FILTRATION",
            "policyDescription": "IP Filtration Policy - Allow Specific IPs",
            "policyStatus": "ACTIVE",
            "args": {
                "IP_FILTRATION_MODE": "WHITE_LISTING",
                "WHITE_LIST_IPS": "192.168.1.10,10.0.0.5",
                "BLACK_LIST_IPS": "" # Empty if white_listing
            }
        }
# ... (other global policy types)


class PublicationFlowValidations:
     @staticmethod
     def get_valid_body() -> Dict[str, Any]:
        return {
            "publicationFlowId": EndpointValidations.PUBLICATION_FLOW_ID, # This might be an existing ID to update
            "remarks": EndpointValidations.generate_random_string(20, prefix="flow_remarks_"),
            "configs": [
                {"publicationFlowConfigId": 1000, "sourceEnv": "DEV", "targetEnv": "STG", "order": 1},
                {"publicationFlowConfigId": 1001, "sourceEnv": "STG", "targetEnv": "SDB", "order": 2},
                {"publicationFlowConfigId": 1002, "sourceEnv": "SDB", "targetEnv": "PRD", "order": 3}
            ]
        }

class RevisionValidations:
    @staticmethod
    def get_valid_body() -> Dict[str, Any]: # Revisions are usually read, not created with full body
        return {} # Or specific fields if updating/querying revisions

class MessageBrokerValidations:
    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        name = EndpointValidations.generate_random_string(prefix="Broker_")
        return {
            "name": name,
            "host": "message-broker.example.com",
            "port": random.choice([5672, 9092]), # RabbitMQ, Kafka defaults
            "username": EndpointValidations.generate_random_string(prefix="broker_user_"),
            "password": EndpointValidations.generate_random_string(16),
            "brokerProvider": random.choice(["RABBIT_MQ", "KAFKA"]),
            "allowedOnDevPortal": random.choice([True, False]),
            "status": "DRAFT",
            "topics": [f"topic_{i}" for i in range(random.randint(1,3))]
        }

class PolicyTemplateValidations:
    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        name = EndpointValidations.generate_random_string(prefix="PolicyTemplate_")
        return {
            "policyTemplateName": name,
            "policyTemplateDesc": f"Description for {name}",
            "requestPolicies": [ApiPolicyValidations.get_valid_request_rate_limiter_policy()],
            "responsePolicies": [] # Example: no response policies
        }

class WorkflowValidations: # Renamed from Wf to Workflow
    @staticmethod
    def get_valid_body() -> Dict[str, Any]: # Generic, depends on specific workflow action
        # Example for a 'performProcessAction' like endpoint
        return {
             "reason": EndpointValidations.generate_random_string(15, prefix="action_reason_"),
             "action": random.choice(["PROCESS_NEXT", "WITHDRAW", "TERMINATE"])
        }
    # Add more specific workflow bodies if needed

class ValidatorFactory:
    validators: Dict[str, Any] = { # Explicitly type hint
        "api-specs": ApiSpecValidations,
        "environments": EnvironmentModelValidations,
        "authenticators": AuthenticatorModelValidations,
        "credentials": CredentialModelValidations, # This key might be part of authenticators or standalone
        "policies": ApiPolicyValidations, # Changed from "policy" for consistency
        "consumers": ConsumerModelValidations,
        "products": ProductModelValidations,
        "plans": PlanModelValidations,
        "subscriptions": SubscriptionModelValidations,
        "global-policies": GlobalPolicyValidations, # Changed from "global_policy"
        "publication-flow-configs": PublicationFlowValidations, # Changed from "publication_flow"
        "revisions": RevisionValidations,
        "message-brokers": MessageBrokerValidations, # Changed from "message_brokers"
        "policy-templates": PolicyTemplateValidations, # Changed from "policy_templates"
        "wf": WorkflowValidations, # For workflow related things
        # Add other endpoint keys and their corresponding validation classes
        "item": ApiSpecValidations, # Default for /item/fields if no specific type
        "default": ApiSpecValidations # A very generic fallback
    }

    @staticmethod
    def get_validator(endpoint_type: Optional[str]):
        if not endpoint_type:
            return ValidatorFactory.validators.get("default")
        return ValidatorFactory.validators.get(endpoint_type.lower())

    @staticmethod
    def get_all_validator_names() -> List[str]:
        return list(ValidatorFactory.validators.keys())

