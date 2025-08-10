# TODO: add other required fields

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Demo JSON Schema",
    "type": "object",
    "required": ["demoId", "demoName", "steps"],
    "properties": {
        "demoId": {"type": "string", "format": "uuid"},
        "demoName": {"type": "string"},
        "demoDescription": {"type": "string"},
        "steps": {
            "type": "object",
            "patternProperties": {
                "^[0-9]+$": {
                    "type": "object",
                    "required": ["title", "url", "details"],
                    "properties": {
                        "title": {"type": "string"},
                        "url": {"type": "string", "format": "uri"},
                        "details": {"type": "string"}
                    }
                }
            },
            "minProperties": 1
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of required DPG names for this demo"
        }
    }
}

metadata_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Demo Metadata Schema",
    "type": "object",
    "required": ["demos"],
    "properties": {
        "demos": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "demoId", "name", "file_name",
                    "description", "version", "steps_count",
                    "created_at", "updated_at",
                    "created_by", "last_modified_by", "deleted", "tags"
                ],
                "properties": {
                    "demoId": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "file_name": {"type": "string"},
                    "description": {"type": "string"},
                    "version": {"type": "integer"},
                    "steps_count": {"type": "integer"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"},
                    "created_by": {"type": "string"},
                    "last_modified_by": {"type": "string"},
                    "deleted": {"type": "boolean"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    }
}
