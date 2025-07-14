# TODO: add other required fields

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Demo JSON Schema",
    "type": "object",
    "required": ["demoName", "steps"],
    "properties": {
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
        }
    }
}
