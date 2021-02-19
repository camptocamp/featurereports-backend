import pytest

from drealcorsereports.models.reports import ReportModel, Report
from datetime import datetime, timezone

ALLOWED_LAYER = "ALLOWED_LAYER"
DENIED_LAYER = "DENIED_LAYER"

@pytest.fixture(scope="function")
@pytest.mark.usefixtures("transact")
def test_data(dbsession):
    report_models = [
        ReportModel(
            name="existing_allowed",
            layer_id=ALLOWED_LAYER,
            custom_field_schema={"test": "test"},
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="tata",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
        ),
        ReportModel(
            name="existing_denied",
            layer_id=DENIED_LAYER,
            custom_field_schema={"test": "test"},
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="tata",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
        ),
    ]
    reports =  [
        Report(
            report_model = report_models[0],
            feature_id= "1234",
            custom_field_values = {"test": "foo"},
            created_by="foo",
            created_at=datetime(2021, 1, 21, 13, 37, tzinfo=timezone.utc),
            updated_by="foo",
            updated_at=datetime(2021, 1, 21, 13, 37, tzinfo=timezone.utc),
        ),
        Report(
            report_model = report_models[0],
            feature_id= "1234",
            custom_field_values = {"test": "bar"},
            created_by="bar",
            created_at=datetime(2021, 1, 22, 13, 37, tzinfo=timezone.utc),
            updated_by="bar",
            updated_at=datetime(2021, 1, 22, 13, 37, tzinfo=timezone.utc),
        ),
        Report(
            report_model = report_models[0],
            feature_id= "abcd",
            custom_field_values = {"test": "baz"},
            created_by="baz",
            created_at=datetime(2021, 1, 23, 13, 37, tzinfo=timezone.utc),
            updated_by="baz",
            updated_at=datetime(2021, 1, 23, 13, 37, tzinfo=timezone.utc),
        ),
    ]
    dbsession.add_all(report_models)
    dbsession.flush()
    dbsession.expire_all()
    yield {
        "report_models": report_models,
        "reports": reports
    }


class TestReportView:
    def test_get_none(self, test_app):
        r = test_app.get("/reports")
        assert r.status_code == 200
        assert r.json == []

    def test_report_bad_id(self, test_app):
        r = test_app.get("/reports/1234", status=422)
        assert r.json == {
            "errors": [
                {
                    "description": "Your id seems malformed",
                    "location": "body",
                    "name": "id",
                }
            ],
            "status": "error",
        }

    def test_report_id(self, test_app, test_data):
        report_id = test_data['reports'][0].id
        test_app.get(f"/reports/{report_id}")
