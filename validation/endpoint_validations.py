"""
Endpoint validation rules based on ModelFactory
"""
import uuid
import random
import string
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


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


class EnvironmentType(Enum):
    DEV = "DEV"
    TEST = "TEST"
    STG = "STG"
    SDB = "SDB"
    PRD = "PRD"


class ConsumerStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"


class ContactType(Enum):
    BUSINESS = "BUSINESS"
    TECHNICAL = "TECHNICAL"
    ADMINISTRATIVE = "ADMINISTRATIVE"


def manipulate_and_create_random_data(body: Any, apiPath: str):
    """
    Manipulate and create random data for both dict and list body types.
    """
    # Convert dict with numeric keys to a list
    if isinstance(body, dict) and all(k.isdigit() for k in body.keys()):
        body = [body[k] for k in sorted(body.keys(), key=int)]

    # Fetch the apiKey and match it with the validator
    if apiPath.startswith("http"):
        apiKey = apiPath.split("/")[-1]
    else:
        segments = apiPath.strip("/").split("/")
        apiKey = segments[-1] if len(segments) == 1 else segments[-2]

    # Match the apiKey with the validator
    validator = ValidatorFactory.get_validator(apiKey)

    if not validator or not hasattr(validator, 'get_valid_body'):
        raise ValueError(f"No valid validator found for apiKey: {apiKey}")

    # Generate random data using the validator
    random_data = validator.get_valid_body()

    # Merge the provided body with the random data
    if isinstance(random_data, list):
        if isinstance(body, list):
            for i, item in enumerate(body):
                if isinstance(item, dict):
                    # Generate a new random item for each iteration
                    random_item = validator.get_valid_body()[i % len(random_data)]
                    for key, value in random_item.items():
                        if key not in item or item[key] is None:
                            item[key] = value
        else:
            raise TypeError("Body must be a list of dictionaries when random_data is a list.")
    elif isinstance(random_data, dict):
        if isinstance(body, dict):
            for key, value in random_data.items():
                if key not in body or body[key] is None:
                    body[key] = value
        elif isinstance(body, list):
            for item in body:
                if isinstance(item, dict):
                    for key, value in random_data.items():
                        if key not in item or item[key] is None:
                            item[key] = value
                else:
                    raise TypeError("List elements must be dictionaries.")
        else:
            raise TypeError("Body must be a dictionary or a list of dictionaries when random_data is a dictionary.")

    return body

# Validation rules based on ModelFactory
class EndpointValidations:
    # Constants from ModelFactory
    DEFAULT_BACKEND_SERVICE_URL = "https://jsonplaceholder.typicode.com"
    DEV_GATEWAY_ENVIRONMENT_ID = "apigw-local01-23122023"
    STG_GATEWAY_ENVIRONMENT_ID = "apigw-local02-123445"
    SDB_GATEWAY_ENVIRONMENT_ID = "apigw-local02-1234456789"
    VALID_TEST_GW_ENV_URL = "https://gw01.test.dgate.digitinary.net"
    DELETED_API_GATEWAY_ENVIRONMENT_ID = "delete-api-gateway"
    PUBLICATION_FLOW_ID = 1000

    @staticmethod
    def generate_random_string(length: int = 12) -> str:
        """Generate a random string similar to ModelFactory.generateRandomString()"""
        return str(uuid.uuid4()).replace("-", "")[:length]

    @staticmethod
    def generate_random_email() -> str:
        """Generate a random email address"""
        return f"user{EndpointValidations.generate_random_string()}@digitinary.com"

    @staticmethod
    def generate_valid_phone() -> str:
        """Generate a valid phone number"""
        return f"123456789"

    @staticmethod
    def generate_valid_version() -> str:
        """Generate a valid API version"""
        return f"{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}"


class ApiSpecValidations:
    """Validation rules for ApiSpec endpoints"""

    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        """Generate a valid API spec body"""
        name = EndpointValidations.generate_random_string()
        return {
            "name": name,
            "description": f"Description for {name}",
            "contextPath": f"/{name}",
            "backendServiceUrl": EndpointValidations.DEFAULT_BACKEND_SERVICE_URL,
            "status": "DRAFT",
            "type": random.choice(list(ApiType)).value,
            "style": random.choice(list(ApiStyle)).value,
            "authType": random.choice(list(AuthenticatorType)).value,
            "metaData": {
                "version": EndpointValidations.generate_valid_version(),
                "owner": EndpointValidations.generate_random_string(),
                "category": "Test Category",
                "tags": [f"tag-{EndpointValidations.generate_random_string()}" for _ in range(3)]
            },
            "addVersionToContextPath": True,
            "predicates": [],
            "requestPolicies": [],
            "responsePolicies": []
        }

    @staticmethod
    def get_invalid_api_spec_bodies() -> List[Dict[str, Any]]:
        """Generate invalid API spec bodies for testing"""
        return [
            # Empty name
            {"name": "", "contextPath": "/test", "type": "PUBLIC", "style": "REST"},
            # Invalid API type
            {"name": "test", "contextPath": "/test", "type": "INVALID", "style": "REST"},
            # Missing required fields
            {"name": "test"},
            # Invalid context path (not starting with /)
            {"name": "test", "contextPath": "test", "type": "PUBLIC", "style": "REST"},
            # Invalid status
            {"name": "test", "contextPath": "/test", "type": "PUBLIC", "style": "REST", "status": "INVALID"}
        ]


class EnvironmentModelValidations:
    """Validation rules for Environment endpoints"""

    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        """Generate a valid environment body"""
        return {
            "name": f"Env-{EndpointValidations.generate_random_string()}",
            "url": EndpointValidations.VALID_TEST_GW_ENV_URL,
            "backendServiceUrls": [EndpointValidations.DEFAULT_BACKEND_SERVICE_URL],
            "type": random.choice(list(EnvironmentType)).value
        }

    @staticmethod
    def get_invalid_environment_bodies() -> List[Dict[str, Any]]:
        """Generate invalid environment bodies for testing"""
        return [
            # Invalid URL
            {"name": "Test", "url": "invalid-url", "type": "DEV", "backendServiceUrls": []},
            # Empty name
            {"name": "", "url": "https://test.com", "type": "DEV", "backendServiceUrls": []},
            # Invalid environment type
            {"name": "Test", "url": "https://test.com", "type": "INVALID", "backendServiceUrls": []},
            # Empty backend service URLs
            {"name": "Test", "url": "https://test.com", "type": "DEV", "backendServiceUrls": []}
        ]

class CredentialModelValidations:
    """Validation rules for Credential endpoints"""

    @staticmethod
    def get_valid_body() -> list:
        """Generate a valid credential body"""
        return [
            {
                "authenticatorType": f"{random.choice(list(AuthenticatorType)).value}",
                "username": f"user-{EndpointValidations.generate_random_string()}",
                "password": "password",
                "clientId": f"client-{EndpointValidations.generate_random_string()}",
                "apiKeyClientName": f"api-key-{EndpointValidations.generate_random_string()}",
                "apiKey": f"api-key-{EndpointValidations.generate_random_string()}",
                "apiKeySecret": f"api-key-secret-{EndpointValidations.generate_random_string()}"
            }
        ]


    @staticmethod
    def get_valid_basic_credential() -> Dict[str, Any]:
        """Generate valid basic credentials"""
        return {
            "authenticatorType": "BASIC",
            "username": f"user-{EndpointValidations.generate_random_string()}",
            "password": "password"
        }

    @staticmethod
    def get_valid_oauth_credential() -> Dict[str, Any]:
        """Generate valid OAuth credentials"""
        return {
            "authenticatorType": "OAUTH",
            "clientId": f"client-{EndpointValidations.generate_random_string()}"
        }

    @staticmethod
    def get_valid_api_key_credential() -> Dict[str, Any]:
        """Generate valid API key credentials"""
        return {
            "authenticatorType": "API_KEY",
            "apiKeyClientName": f"api-key-{EndpointValidations.generate_random_string()}"
        }


class AuthenticatorModelValidations:
    """Validation rules for Authenticator endpoints"""

    @staticmethod
    def get_valid_body(environment_id: str = None, auth_type: str = None, tokenUrl:str = None, backendServiceUrls=None) -> Dict[str, Any]:
        """Generate a valid authenticator body"""
        if backendServiceUrls is None:
            backendServiceUrls = []
        auth_type = auth_type or random.choice(list(AuthenticatorType)).value
        body = {
            "name": f"{auth_type}-Auth-{EndpointValidations.generate_random_string()}",
            "type": auth_type,
            "tokenUrl" : tokenUrl or f"https://{auth_type.lower()}-token-url.com",
            "backendServiceUrls": backendServiceUrls,
        }
        if environment_id:
            body["environmentModel"] = environment_id
        return body


class ApiPolicyValidations:
    """Validation rules for API Policy endpoints"""

    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        """Generate a valid API policy body (defaulting to request rate limiter)"""
        return ApiPolicyValidations.get_valid_request_rate_limiter_policy()

    @staticmethod
    def get_valid_request_rate_limiter_policy() -> Dict[str, Any]:
        """Generate valid request rate limiter policy"""
        return {
            "policyName": "REQUEST_RATE_LIMITER",
            "httpExchange": "REQUEST",
            "order": 1,
            "args": {
                "PER_SECONDS": "10",
                "NO_OF_REQUESTS": "7"
            }
        }

    @staticmethod
    def get_valid_response_cache_policy() -> Dict[str, Any]:
        """Generate valid response cache policy"""
        return {
            "policyName": "RESPONSE_BODY_CACHE",
            "httpExchange": "RESPONSE",
            "order": 1,
            "args": {
                "TIME_TO_LIVE": "13",
                "TIME_UNIT": "sec",
                "UNLIMITED": "false"
            }
        }

    @staticmethod
    def get_valid_request_quota_policy() -> Dict[str, Any]:
        """Generate valid request quota policy"""
        return {
            "policyName": "REQUEST_QUOTA",
            "httpExchange": "RESPONSE",
            "order": 1,
            "args": {
                "QUOTA": "500",
                "TIME_UNIT": "4"
            }
        }


class ConsumerModelValidations:
    """Validation rules for Consumer endpoints"""

    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        """Generate a valid consumer body"""
        random_string = EndpointValidations.generate_random_string()
        return {
            "consumerKey": f"Consumer-{random_string}",
            "name": f"Consumer-{random_string}",
            "segment": "Goverment",
            "status": random.choice(list(ConsumerStatus)).value,
            "logo": "https://www.digitinary.com/logo.png",
            "consumerType": "GENERAL",
            "organization": {
                "companyRegistrationNo": "123456789",
                "legalEntityIdentification": "123456789",
                "businessName": f"Business-{random_string}",
                "legalEntityName": f"Legal-{random_string}"
            },
            "contacts": [{
                "contactType": random.choice(list(ContactType)).value,
                "firstName": f"First-{random_string}",
                "lastName": f"Last-{random_string}",
                "jobTitle": f"Job-{random_string}",
                "email": EndpointValidations.generate_random_email(),
                "mobileNo": EndpointValidations.generate_valid_phone()
            }],
            "users": [{
                "firstName": f"First-{random_string}",
                "lastName": f"Last-{random_string}",
                "email": EndpointValidations.generate_random_email(),
                "emailVerified": True,
                "owner": True,
                "agreementTerms": True
            }]
        }


class ProductModelValidations:
    """Validation rules for Product endpoints"""

    @staticmethod
    def get_valid_body(api_spec_ids: List[str] = None) -> Dict[str, Any]:
        """Generate a valid product body"""
        return {
            "name": EndpointValidations.generate_random_string(),
            "desc": f"Description for {EndpointValidations.generate_random_string()}",
            "version": "1.0.0",
            "apiSpecs": api_spec_ids or [],
            "segment": "Goverment",
            "premium": True,
            "status": "DRAFT"
        }


class PlanModelValidations:
    """Validation rules for Plan endpoints"""

    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        """Generate a valid plan body"""
        return {
            "name": EndpointValidations.generate_random_string(),
            "desc": f"Description for {EndpointValidations.generate_random_string()}",
            "definitionType": "STANDARD",
            "subscriptionPeriodOptions": ["MONTHLY"],
            "priceType": "USAGE_BASED_CHARGES",
            "renewalTypeOptions": ["AUTO"],
            "premium": True,
            "planStatus": "DRAFT"
        }


class SubscriptionModelValidations:
    """Validation rules for Subscription endpoints"""

    @staticmethod
    def get_valid_body(plan_id: int = None, project_name: str = None) -> Dict[str, Any]:
        """Generate a valid subscription body"""
        body = {
            "projectName": project_name or EndpointValidations.generate_random_string(),
            "renewalType": "MANUAL",
            "trial": False,
            "subscriptionPeriod": "MONTHLY",
            "runtimeConfigPublicationModel": {
                "objectId": "apigw_dev_1_dev",
                "actionType": "ADD",
                "environment": {
                    "environmentId": EndpointValidations.DEV_GATEWAY_ENVIRONMENT_ID,
                    "type": "DEV"
                }
            }
        }
        if plan_id:
            body["planId"] = plan_id
        return body

class GlobalPolicyValidations:
    """Validation rules for Global Policy endpoints"""

    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        """Generate a valid global policy body (defaulting to IP filtration)"""
        return GlobalPolicyValidations.get_valid_ip_filtration_policy()

    @staticmethod
    def get_valid_ip_filtration_policy() -> Dict[str, Any]:
        """Generate valid IP filtration policy"""
        return {
            "globalPolicyName": "IP_FILTRATION",
            "policyDescription": "IP Filtration Policy",
            "args": {
                "IP_FILTRATION_MODE": "WHITE_LISTING",
                "WHITE_LIST_IPS": "192.168.0.2",
                "BLACK_LIST_IPS": "192.168.0.500"
            }
        }

    @staticmethod
    def get_valid_json_path_depth_policy() -> Dict[str, Any]:
        """Generate valid JSON path depth policy"""
        return {
            "globalPolicyName": "JSON_PATH_DEPTH",
            "policyDescription": "Json Path Depth Policy",
            "policyStatus": "ACTIVE",
            "args": {
                "JSON_PATH_DEPTH": "5"
            }
        }


class PublicationFlowValidations:
    """Validation rules for Publication Flow endpoints"""

    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        """Generate a valid publication flow body"""
        return {
            "publicationFlowId": EndpointValidations.PUBLICATION_FLOW_ID,
            "remarks": EndpointValidations.generate_random_string(),
            "configs": [
                {
                    "publicationFlowConfigId": 1000,
                    "sourceEnv": "DEV",
                    "targetEnv": "STG",
                    "order": 1
                },
                {
                    "publicationFlowConfigId": 1001,
                    "sourceEnv": "STG",
                    "targetEnv": "SDB",
                    "order": 2
                },
                {
                    "publicationFlowConfigId": 1002,
                    "sourceEnv": "SDB",
                    "targetEnv": "PRD",
                    "order": 3
                }
            ]
        }

class RevisionValidations:
    """Validation rules for Revision endpoints"""

    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        """Generate a valid revision body"""
        return {
            "objectId": EndpointValidations.generate_random_string(),
            "objectType": random.choice(["GATEWAY_ENVIRONMENT", "API_SPEC", "AUTHENTICATOR", "EXCHANGE_POLICY", "GLOBAL_POLICY", "CONSUMER", "SUBSCRIPTION", "MONETIZATION_PRODUCT", "MONETIZATION_PLAN", "MESSAGE_BROKER", "STATIC_RESPONSE", "AUTHENTICATOR_CREDENTIALS"]),
            # Add other fields based on the RevisionChangeModel
        }

class MessageBrokerValidations:
    """Validation rules for Message Broker endpoints"""

    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        """Generate a valid message broker body"""
        return {
            "name": EndpointValidations.generate_random_string(),
            "host": "localhost",
            "port": random.randint(1000, 9999),
            "username": EndpointValidations.generate_random_string(),
            "password": EndpointValidations.generate_random_string(),
            "brokerProvider": random.choice(["RABBIT_MQ", "KAFKA"]),
            # Add other fields based on the MessageBrokerModel
        }

class PolicyTemplateValidations:
    """Validation rules for Policy Template endpoints"""

    @staticmethod
    def get_valid_body() -> Dict[str, Any]:
        """Generate a valid policy template body"""
        return {
            "policyTemplateName": EndpointValidations.generate_random_string(),
            "policyTemplateDesc": EndpointValidations.generate_random_string(),
            "requestPolicies": [ApiPolicyValidations.get_valid_request_rate_limiter_policy()],
            "responsePolicies": [ApiPolicyValidations.get_valid_response_cache_policy()],
            # Add other fields based on the ExchangePolicyTemplateModel
        }

class WorkflowValidations:
    """Validation rules for Workflow endpoints"""

    @staticmethod
    def get_valid_process_action_body() -> Dict[str, Any]:
        """Generate a valid workflow process action body"""
        return {
            "reason": EndpointValidations.generate_random_string(),
            "action": random.choice(["PROCESS_NEXT", "WITHDRAW", "TERMINATE"]),
        }

class ValidatorFactory:
    validators = {
        "api-specs": ApiSpecValidations,
        "environments": EnvironmentModelValidations,
        "authenticators": AuthenticatorModelValidations,
        "credentials": CredentialModelValidations,
        "policy": ApiPolicyValidations,
        "consumers": ConsumerModelValidations,
        "products": ProductModelValidations,
        "plans": PlanModelValidations,
        "subscriptions": SubscriptionModelValidations,
        "global_policy": GlobalPolicyValidations,
        "publication_flow": PublicationFlowValidations,
        "revisions": RevisionValidations,
        "message_brokers": MessageBrokerValidations,
        "policy_templates": PolicyTemplateValidations,
        "wf": WorkflowValidations
    }
    @staticmethod
    def get_validator(endpoint_type: str):
        """Get the appropriate validator based on endpoint type"""
        return ValidatorFactory.validators.get(endpoint_type.lower())

    @staticmethod
    def get_all_validator_names() -> List[str]:
        """Get all available validator names"""
        return list(ValidatorFactory.validators.keys())