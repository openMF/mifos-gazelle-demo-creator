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
                        "details": {"type": "string"},
                    },
                }
            },
            "minProperties": 1,
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of required DPG names for this demo",
        },
    },
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
                    "demoId",
                    "name",
                    "file_name",
                    "description",
                    "version",
                    "steps_count",
                    "created_at",
                    "updated_at",
                    "created_by",
                    "last_modified_by",
                    "deleted",
                    "tags",
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
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
            },
        }
    },
}

DPG_DEFAULT_CONFIG = {
    "general": {
        "mode": "deploy",
        "GAZELLE_DOMAIN": "mifos.gazelle.test",
        "GAZELLE_VERSION": "1.1.0",
    },
    "environment": {"user": "yash-sharma"},
    "mysql": {
        "MYSQL_SERVICE_NAME": "mysql",
        "MYSQL_SERVICE_PORT": "3306",
        "LOCAL_PORT": "3307",
        "MAX_WAIT_SECONDS": "60",
        "MYSQL_HOST": "127.0.0.1",
    },
    "infra": {
        "enabled": "false",
        "INFRA_NAMESPACE": "infra",
        "INFRA_RELEASE_NAME": "infra",
    },
    "mifosx": {
        "enabled": "true",
        "MIFOSX_NAMESPACE": "mifosx",
        "MIFOSX_REPO_DIR": "mifosx",
        "MIFOSX_BRANCH": "gazelle-1.1.0",
        "MIFOSX_REPO_LINK": "https://github.com/openMF/mifosx-docker.git",
    },
    "vnext": {
        "enabled": "true",
        "VNEXTBRANCH": "beta1",
        "VNEXTREPO_DIR": "vnext",
        "VNEXT_NAMESPACE": "vnext",
        "VNEXT_REPO_LINK": "https://github.com/mojaloop/platform-shared-tools.git",
    },
    "phee": {
        "enabled": "true",
        "PHBRANCH": "master",
        "PHREPO_DIR": "phlabs",
        "PH_NAMESPACE": "paymenthub",
        "PH_RELEASE_NAME": "phee",
        "PH_REPO_LINK": "https://github.com/openMF/ph-ee-env-labs.git",
        "PH_EE_ENV_TEMPLATE_REPO_LINK": "https://github.com/openMF/ph-ee-env-template.git",
        "PH_EE_ENV_TEMPLATE_REPO_BRANCH": "v1.13.0-gazelle-1.1.0",
        "PH_EE_ENV_TEMPLATE_REPO_DIR": "ph_template",
    },
}
