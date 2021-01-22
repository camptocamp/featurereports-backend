from datetime import datetime, timezone
from uuid import uuid4

import pytest
from drealcorsereports.models.reports import ReportModel
from pyramid.httpexceptions import HTTPBadRequest


@pytest.fixture(scope="function")
@pytest.mark.usefixtures("dbsession", "transact")
def test_data(dbsession, transact):
    del transact
    report_models = [
        ReportModel(
            name="existing",
            layer_id="test_layer",
            custom_field_schema={"test": "test"},
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="tata",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
        )
    ]
    dbsession.add_all(report_models)
    dbsession.flush()
    dbsession.expire_all()
    yield {
        "report_models": report_models,
    }


@pytest.mark.usefixtures("transact")
class TestAdminReportModelView:
    def test_collection_get(self, test_app, test_data):
        rm = test_data["report_models"][0]
        r = test_app.get("/admin/report_models", status=200)
        assert r.json == [
            {
                "id": str(rm.id),
                "name": "existing",
                "layer_id": "test_layer",
                "custom_field_schema": {"test": "test"},
                "created_by": "toto",
                "created_at": "2021-01-22T13:33:00+00:00",
                "updated_by": "tata",
                "updated_at": "2021-01-22T13:34:00+00:00",
            }
        ]

    def test_collection_get_empty(self, test_app):
        r = test_app.get("/admin/report_models", status=200)
        assert r.json == []

    def test_collection_post(self, test_app, dbsession):
        payload = {
            "name": "new",
            "custom_field_schema": {"test": "test"},
            "layer_id": "test_layer",
        }
        r = test_app.post_json(
            "/admin/report_models",
            payload,
            headers={
                "sec-username": "toto",
            },
            status=201,
        )
        report_model = dbsession.query(ReportModel).get(r.json["id"])
        assert report_model.name == "new"
        assert report_model.custom_field_schema == {"test": "test"}
        assert report_model.layer_id == "test_layer"
        assert report_model.created_by == "toto"
        assert isinstance(report_model.created_at, datetime)
        assert report_model.created_at.tzinfo is not None
        assert report_model.updated_by == "toto"
        assert isinstance(report_model.updated_at, datetime)
        assert report_model.updated_at.tzinfo is not None

    def test_collection_post_name_unique_validator(self, test_app, dbsession):
        payload = {
            "name": "new",
            "custom_field_schema": {"test": "test"},
            "layer_id": "test_layer",
        }
        r = test_app.post_json(
            "/admin/report_models",
            payload,
            headers={
                "sec-username": "toto",
            },
            status=201,
        )
        report_model = dbsession.query(ReportModel).get(r.json["id"])
        assert report_model.name == "new"

        r = test_app.post_json(
            "/admin/report_models",
            payload,
            headers={
                "sec-username": "toto",
            },
            status=400,
        )
        assert r.json == {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "name",
                    "description": ["Report model named new already exists."],
                }
            ],
        }

    def test_get(self, test_app, test_data):
        rm = test_data["report_models"][0]
        r = test_app.get(f"/admin/report_models/{rm.id}", status=200)
        assert r.json == {
            "id": str(rm.id),
            "name": "existing",
            "layer_id": "test_layer",
            "custom_field_schema": {"test": "test"},
            "created_by": "toto",
            "created_at": "2021-01-22T13:33:00+00:00",
            "updated_by": "tata",
            "updated_at": "2021-01-22T13:34:00+00:00",
        }

    def test_get_not_found(self, test_app):
        test_app.get(f"/admin/report_models/{uuid4()}", status=404)

    def test_put(self, test_app, test_data):
        rm = test_data["report_models"][0]
        updated_at = rm.updated_at
        r = test_app.put_json(
            f"/admin/report_models/{rm.id}",
            {
                "id": str(rm.id),
                "name": "updated",
                "layer_id": "test_layer",
                "custom_field_schema": {"changed": "changed"},
            },
            headers={
                "sec-username": "tata",
            },
            status=200,
        )
        assert r.json["id"] == str(rm.id)
        assert rm.name == "updated"
        assert rm.layer_id == "test_layer"
        assert rm.custom_field_schema == {"changed": "changed"}
        assert rm.updated_by == "tata"
        assert rm.updated_at != updated_at

    def test_put_not_found(self, test_app):
        id = uuid4()
        test_app.put_json(
            f"/admin/report_models/{id}",
            {
                "id": str(id),
                "name": "updated",
                "layer_id": "test_layer",
                "custom_field_schema": {"changed": "changed"},
            },
            headers={
                "sec-username": "tata",
            },
            status=404,
        )

    def test_delete(self, test_app, dbsession, test_data):
        rm = test_data["report_models"][0]
        test_app.delete(f"/admin/report_models/{rm.id}", status=204)
        assert len(dbsession.query(ReportModel).all()) == 0

    def test_delete_not_found(self, test_app):
        test_app.delete(f"/admin/report_models/{uuid4()}", status=404)
