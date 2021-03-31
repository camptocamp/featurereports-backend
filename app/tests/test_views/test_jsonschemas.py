from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from drealcorsereports.models.reports import (
    FieldTypeEnum,
    ReportModel,
    ReportModelCustomField,
)

ALLOWED_LAYER = "ALLOWED_LAYER"
DENIED_LAYER = "DENIED_LAYER"


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("dbsession", "transact")
def test_data(dbsession, transact):
    del transact
    report_models = [
        ReportModel(
            name="existing_allowed",
            layer_id=ALLOWED_LAYER,
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="tata",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
            custom_fields=[
                ReportModelCustomField(
                    name="category",
                    type=FieldTypeEnum.enum,
                    enum=["category1", "category2"],
                    required=True,
                ),
                ReportModelCustomField(
                    name="date",
                    type=FieldTypeEnum.date,
                    required=True,
                ),
                ReportModelCustomField(
                    name="number",
                    type=FieldTypeEnum.number,
                    required=True,
                ),
                ReportModelCustomField(
                    name="boolean",
                    type=FieldTypeEnum.boolean,
                    required=True,
                ),
                ReportModelCustomField(
                    name="file",
                    type=FieldTypeEnum.file,
                    required=False,
                ),
                ReportModelCustomField(
                    name="commentaire",
                    type=FieldTypeEnum.string,
                    required=False,
                ),
            ],
        ),
    ]
    dbsession.add_all(report_models)
    dbsession.flush()
    dbsession.expire_all()
    yield {
        "report_models": report_models,
    }


@pytest.fixture(scope="class")
def patch_is_user_reader_on_layer():
    def is_user_admin_on_layer(user_id, layer_id):
        del user_id
        return layer_id == ALLOWED_LAYER

    with patch(
        "drealcorsereports.views.jsonschemas.is_user_reader_on_layer",
        side_effect=is_user_admin_on_layer,
    ) as rules_mock:
        yield rules_mock


@pytest.mark.usefixtures("test_data", "patch_is_user_reader_on_layer")
class TestJsonSchemasView:
    def test_get_success(self, test_app, test_data):
        report_model = test_data["report_models"][0]

        r = test_app.get(
            "/jsonschemas",
            status=200,
        )
        assert r.json == {
            str(report_model.id): {
                "id": str(report_model.id),
                "name": str(report_model.name),
                "JSONSchema": {
                    "$ref": "#/definitions/ExtendedReportSchema",
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "definitions": {
                        "CustomFieldsSchema": {
                            "type": "object",
                            "required": [
                                "boolean",
                                "category",
                                "date",
                                "number",
                            ],
                            "properties": {
                                "category": {
                                    "title": "category",
                                    "type": "string",
                                    "enum": ["category1", "category2"],
                                },
                                "date": {
                                    "title": "date",
                                    "type": "string",
                                    "format": "date",
                                },
                                "number": {
                                    "title": "number",
                                    "type": "number",
                                    "format": "decimal",
                                },
                                "boolean": {
                                    "title": "boolean",
                                    "type": "boolean",
                                },
                                "file": {
                                    "title": "file",
                                    "type": "string",
                                },
                                "commentaire": {
                                    "title": "commentaire",
                                    "type": "string",
                                },
                            },
                            "additionalProperties": False,
                        },
                        "ExtendedReportSchema": {
                            "type": "object",
                            "required": ["feature_id", "report_model_id"],
                            "properties": {
                                "id": {
                                    "title": "id",
                                    "type": "string",
                                    "ui:widget": "hidden",
                                },
                                "report_model_id": {
                                    "title": "report_model_id",
                                    "type": "string",
                                    "default": str(report_model.id),
                                    "ui:widget": "hidden",
                                },
                                "feature_id": {
                                    "title": "feature_id",
                                    "type": "string",
                                    "ui:widget": "hidden",
                                },
                                "custom_field_values": {
                                    "$ref": "#/definitions/CustomFieldsSchema",
                                    "type": "object",
                                    "ui:order": [
                                        "category",
                                        "date",
                                        "number",
                                        "boolean",
                                        "file",
                                        "commentaire",
                                    ],
                                },
                            },
                            "additionalProperties": False,
                        },
                    },
                },
                "UISchema": {
                    "custom_field_values": {
                        "ui:order": [
                            "category",
                            "date",
                            "number",
                            "boolean",
                            "file",
                            "commentaire",
                        ],
                    },
                    "feature_id": {
                        "ui:widget": "hidden",
                    },
                    "report_model_id": {
                        "ui:widget": "hidden",
                    },
                    "id": {
                        "ui:widget": "hidden",
                    },
                    "ui:order": [
                        "id",
                        "feature_id",
                        "report_model_id",
                        "custom_field_values",
                    ],
                },
            },
        }
