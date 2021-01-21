from datetime import datetime
from uuid import uuid4

import pytest
from drealcorsereports.models.reports import ReportModel
from pyramid.httpexceptions import HTTPBadRequest


class TestAdminReportModelView:
    def test_get_info_empty(self, test_app):
        r = test_app.get("/admin/report_models")
        assert r.status_code == 200
        assert r.json == []

    @pytest.mark.usefixtures("transact")
    def test_posting_minimal_model(self, test_app):
        r_id = uuid4()
        payload = {
            "id": str(r_id),
            "name": "test",
            "custom_field_schema": {"test": "test"},
            "layer_id": "test_layer",
            "created_by": "toto",
            "created_at": str(datetime.now()),
        }
        r = test_app.post_json("/admin/report_models", payload)
        assert r.status_code == 201

    def test_posting_twice_fail(self, test_app):
        r_id = uuid4()
        payload = {
            "id": str(r_id),
            "name": "test",
            "custom_field_schema": {"test": "test"},
            "layer_id": "test_layer",
            "created_by": "toto",
            "created_at": str(datetime.now()),
        }
        r = test_app.post_json("/admin/report_models", payload)
        assert r.status_code == 201
        with pytest.raises(HTTPBadRequest) as e:
            test_app.post_json("/admin/report_models", payload)
            assert str(e.value) == "Cannot register your report model."

    @pytest.mark.usefixtures("transact")
    def test_delete(self, test_app, dbsession):
        rm_id = uuid4()
        rm = ReportModel(
            id=rm_id,
            name="test",
            custom_field_schema={"test": "test"},
            layer_id="test_layer",
            created_by="toto",
        )
        dbsession.add(rm)
        dbsession.commit()
        result = test_app.delete(f"/admin/report_models/{rm_id}")
        assert result.status_code == 204
        assert len(dbsession.query(ReportModel).all()) == 0
