import json
from src.v3.core.schemas.identity import Tenant, User, Session, Person, Organization
from src.v3.core.schemas.financial import InvoiceData, InvoiceLineItem
from src.v3.core.schemas.internal import SystemPersonaPayload, Heartbeat

def generate_openapi_spec():
    # 1. Base OpenAPI Skeleton
    openapi_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "Menir Core API",
            "version": "5.2.0",
            "description": "Control Plane Open Protocol for Menir Zero-Trust Architecture.",
            "contact": {"name": "LibLabs Architecture Team"}
        },
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Tenant JWT used for Galvanic Isolation Context propagation (e.g. SANTOS vs BECO)."
                }
            },
            "schemas": {}
        },
        "security": [{"BearerAuth": []}],
        "paths": {
            "/status": {
                "get": {
                    "summary": "Health and Concurrency Status",
                    "description": "Returns the Watchdog and Semaphore queue saturation limits.",
                    "responses": {
                        "200": {"description": "System Online Payload"}
                    }
                }
            },
            "/command": {
                "post": {
                    "summary": "Unified Command Pipeline",
                    "description": "Executes a multi-modal payload through MenirLogos into the Semaphore command bus.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "intent": {"type": "string"},
                                        "origin": {
                                            "type": "string",
                                            "default": "WEB_UI"
                                        }
                                    },
                                    "required": ["intent"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "Command Enqueued"},
                        "403": {"description": "Tenant Forgery/Isolation Breach"},
                        "504": {"description": "Semaphore Exhaustion (30s TTL)"}
                    }
                }
            }
        }
    }

    # 2. Add Pydantic Schemas
    schemas = [
        Tenant, User, Session, Person, Organization, 
        InvoiceData, InvoiceLineItem, 
        SystemPersonaPayload, Heartbeat
    ]
    
    # Generate schemas and merge definition references
    # Pydantic JSON schema often embeds sub-schemas inside "$defs". 
    # We will lift those out to components/schemas
    for schema_cls in schemas:
        schema_dict = schema_cls.model_json_schema()
        
        # Extract and assign main schema
        schema_name = schema_cls.__name__
        model_defs = schema_dict.pop("$defs", {})
        
        # Add sub schemas
        for def_name, def_schema in model_defs.items():
            if def_name not in openapi_spec["components"]["schemas"]:
                openapi_spec["components"]["schemas"][def_name] = def_schema
        
        # Add main schema
        openapi_spec["components"]["schemas"][schema_name] = schema_dict

    # Note: Pydantic V2 references use #/$defs/Name. OpenAPI 3 standard prefers #/components/schemas/Name.
    # We do a dirty string replace over the whole JSON to convert references.
    spec_str = json.dumps(openapi_spec, indent=2)
    spec_str = spec_str.replace("#/$defs/", "#/components/schemas/")

    # Output to File
    output_path = "menir_v3_spec.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(spec_str)
        
    print(f"✅ Native OpenAPI 3.1.0 Specification successfully generated at {output_path}")

if __name__ == "__main__":
    generate_openapi_spec()
