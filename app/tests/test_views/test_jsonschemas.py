import json
import os
from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID

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
            id=UUID("{12345678-1234-5678-1234-567812345678}"),
            name="model_one",
            title="Model 1",
            layer_id=ALLOWED_LAYER,
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="tata",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
            custom_fields=[
                ReportModelCustomField(
                    name="category",
                    title="Catégorie",
                    type=FieldTypeEnum.enum,
                    enum=["category1", "category2"],
                    required=True,
                ),
                ReportModelCustomField(
                    name="date",
                    title="Date",
                    type=FieldTypeEnum.date,
                    required=True,
                ),
                ReportModelCustomField(
                    name="number",
                    title="Nombre",
                    type=FieldTypeEnum.number,
                    required=True,
                ),
                ReportModelCustomField(
                    name="boolean",
                    title="Booléen",
                    type=FieldTypeEnum.boolean,
                    required=True,
                ),
                ReportModelCustomField(
                    name="file",
                    title="File",
                    type=FieldTypeEnum.file,
                    required=False,
                ),
                ReportModelCustomField(
                    name="commentaire",
                    title="Commentaire",
                    type=FieldTypeEnum.string,
                    required=False,
                ),
            ],
        ),
        ReportModel(
            id=UUID("{12345678-1234-5678-1234-567812345679}"),
            name="model_two",
            title="Model 2",
            layer_id=ALLOWED_LAYER,
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="tata",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
            custom_fields=[
                ReportModelCustomField(
                    name="commentaire",
                    title="Commentaire",
                    type=FieldTypeEnum.string,
                    required=False,
                ),
            ],
        ),
        ReportModel(
            id=UUID("{12345678-1234-5678-1234-567812345675}"),
            name="model_three",
            title="Model 3",
            layer_id=DENIED_LAYER,
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="tata",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
            custom_fields=[
                ReportModelCustomField(
                    name="commentaire",
                    title="Commentaire",
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
def patch_is_user_writer_on_layer():
    def is_user_writer_on_layer(user_id, layer_id):
        del user_id
        return layer_id == ALLOWED_LAYER

    with patch(
        "drealcorsereports.views.jsonschemas.is_user_writer_on_layer",
        side_effect=is_user_writer_on_layer,
    ) as rules_mock:
        yield rules_mock

@pytest.fixture(scope="class")
def patch_is_user_reader_on_layer():
    def is_user_reader_on_layer(user_id, layer_id):
        del user_id
        return layer_id == ALLOWED_LAYER

    with patch(
        "drealcorsereports.views.jsonschemas.is_user_reader_on_layer",
        side_effect=is_user_reader_on_layer,
    ) as rules_mock:
        yield rules_mock

@pytest.mark.usefixtures("test_data", "patch_is_user_writer_on_layer", "patch_is_user_reader_on_layer")
class TestJsonSchemasView:
    def test_get_success(self, test_app, test_data):
        r = test_app.get(
            "/jsonschemas",
            status=200,
        )

        with open(os.path.join(os.path.dirname(__file__), "jsonschema.json"), "r") as f:
            # json.dump(r.json, f, indent=4)
            expected = json.load(f)

        assert r.json == expected
