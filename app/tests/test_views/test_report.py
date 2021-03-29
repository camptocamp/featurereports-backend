from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4
from freezegun import freeze_time

import pytest
from drealcorsereports.models.reports import (
    ReportModel,
    ReportModelCustomField,
    FieldTypeEnum,
    Report,
)

ALLOWED_LAYER = "ALLOWED_LAYER"
DENIED_LAYER = "DENIED_LAYER"


@pytest.fixture(scope="class")
def patch_check_user_right():
    def check_user_right(user_id, layer_id, level_required):
        del user_id
        del level_required
        return layer_id == ALLOWED_LAYER

    with patch(
        "drealcorsereports.security.check_user_right",
        side_effect=check_user_right,
    ) as right_mock:
        yield right_mock


@pytest.fixture(scope="function")
@pytest.mark.usefixtures(
    "dbsession",
    "transact",
)
def test_data(dbsession, transact):
    del transact
    rm1 = ReportModel(
        name="existing_bar",
        layer_id=ALLOWED_LAYER,
        created_by="toto",
        created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        updated_by="tata",
        updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
        custom_fields=[
            ReportModelCustomField(
                name="commentaire",
                type=FieldTypeEnum.string,
            )
        ],
    )
    rm2 = ReportModel(
        name="existing_foo",
        layer_id=DENIED_LAYER,
        created_by="toto",
        created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        updated_by="tata",
        updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
        custom_fields=[
            ReportModelCustomField(
                name="something",
                type=FieldTypeEnum.string,
            )
        ],
    )
    dbsession.add_all([rm1, rm2])
    dbsession.flush()
    r1 = Report(
        feature_id=str(uuid4()),
        report_model=rm1,
        custom_field_values={"commentaire": "foo"},
        created_by="foo",
        created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        updated_by="foo",
        updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
    )
    r2 = Report(
        feature_id=str(uuid4()),
        report_model=rm2,
        custom_field_values={"commentaire": "bar"},
        created_by="bar",
        created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        updated_by="bar",
        updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
    )
    r3 = Report(
        feature_id=str(uuid4()),
        report_model=rm2,
        custom_field_values={"something": "foo"},
        created_by="foo",
        created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        updated_by="foo",
        updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
    )
    r4 = Report(
        feature_id=str(uuid4()),
        report_model=rm2,
        custom_field_values={"something": "foo"},
        created_by="bar",
        created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        updated_by="bar",
        updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
    )
    dbsession.add_all([r1, r2, r3, r4])
    dbsession.flush()
    dbsession.expire_all()
    yield {"report_models": [rm1, rm2], "reports": [r1, r2, r3, r4]}


@pytest.mark.usefixtures("patch_check_user_right")
class TestReportView:
    def test_collection_get_forbidden(self, test_app, test_data):
        test_app.get(
            f"/reports?layer_id={DENIED_LAYER}&feature_id={test_data['reports'][0].id}",
            headers={
                "Accept": "application/json",
                "sec-username": "bob",
                "sec-roles": "ROLE_USER",
            },
            status=403,
        )

    def test_collection_get_no_feature_id(self, test_app, test_data):
        test_app.get(
            f"/reports?layer_id={ALLOWED_LAYER}",
            headers={
                "Accept": "application/json",
                "sec-username": "bob",
                "sec-roles": "ROLE_USER",
            },
            status=400,
        )

    def test_collection_get_success(self, test_app, test_data):
        r = test_app.get(
            f"/reports?layer_id={ALLOWED_LAYER}&feature_id={test_data['reports'][0].feature_id}",
            headers={
                "Accept": "application/json",
                "sec-username": "bob",
                "sec-roles": "ROLE_USER",
            },
            status=200,
        )
        assert isinstance(r.json, list)
        assert len(r.json) == 1

    def test_collection_post_success(self, test_app, test_data):
        f_id = uuid4()
        r = test_app.post_json(
            "/reports",
            {
                "feature_id": str(f_id),
                "report_model_id": str(test_data["report_models"][0].id),
                "custom_field_values": {"commentaire": "foo"},
            },
            headers={
                "Accept": "application/json",
                "sec-roles": "ROLE_USER",
                "sec-username": "bob",
            },
            status=201,
        )
        assert r.headers["content-location"].startswith("reports")
        assert r.json["feature_id"] == str(f_id)

    def test_collection_post_layer_denied(self, test_app, test_data, dbsession):
        report_model = (
            dbsession.query(ReportModel).filter(ReportModel.layer_id == DENIED_LAYER)
        ).first()
        assert report_model is not None

        r = test_app.post_json(
            "/reports",
            {
                "feature_id": str(uuid4()),
                "report_model_id": str(report_model.id),
                "custom_field_values": {"commentaire": "foo"},
            },
            headers={
                "Accept": "application/json",
                "sec-roles": "ROLE_USER",
                "sec-username": "bob",
            },
            status=400,
        )
        assert r.json == {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "report_model_id",
                    "description": ["You're not writer on layer DENIED_LAYER."],
                }
            ],
        }

    def test_collection_post_wrong_custom_fields(self, test_app, test_data):
        f_id = uuid4()
        r = test_app.post_json(
            "/reports",
            {
                "feature_id": str(f_id),
                "report_model_id": str(test_data["report_models"][0].id),
                "custom_field_values": {"this_is_a_wrong_field": "foo"},
            },
            headers={
                "Accept": "application/json",
                "sec-roles": "ROLE_USER",
                "sec-username": "bob",
            },
            status=400,
        )
        assert r.json == {
            "errors": [
                {
                    "location": "body",
                    "name": "custom_field_values",
                    "description": ["Unexpected field this_is_a_wrong_field"],
                }
            ],
            "status": "error",
        }

    def test_get_forbidden(self, test_app, test_data, dbsession):
        report = (
            dbsession.query(Report)
            .join(ReportModel)
            .filter(ReportModel.layer_id == DENIED_LAYER)
        ).first()
        assert report is not None

        test_app.get(
            f"/reports/{report.id}",
            headers={
                "Accept": "application/json",
                "sec-roles": "ROLE_USER",
                "sec-username": "bob",
            },
            status=403,
        )

    def test_get_success(self, test_app, test_data):
        report = test_data["reports"][0]
        r = test_app.get(
            f"/reports/{report.id}",
            headers={
                "Accept": "application/json",
                "sec-roles": "ROLE_USER",
                "sec-username": "bob",
            },
            status=200,
        )
        assert r.json == {
            "id": str(report.id),
            "feature_id": str(report.feature_id),
            "report_model_id": str(report.report_model_id),
            "created_at": "2021-01-22T13:33:00+00:00",
            "updated_by": "foo",
            "created_by": "foo",
            "updated_at": "2021-01-22T13:34:00+00:00",
            "custom_field_values": {"commentaire": "foo"},
        }

    def test_get_not_found(self, test_app):
        r = test_app.get(
            f"/reports/{uuid4()}",
            headers={
                "Accept": "application/json",
                "sec-roles": "ROLE_USER",
                "sec-username": "bob",
            },
            status=404,
        )
        assert sorted(list(r.json.keys())) == sorted(["code", "message", "title"])
        assert r.json["code"] == "404 Not Found"
        assert r.json["title"] == "Not Found"
        assert r.json["message"].startswith("The resource could not be found")

    @freeze_time("2020-01-01")
    def test_put_success(self, test_app, test_data):
        r = test_app.put_json(
            f"/reports/{test_data['reports'][0].id}",
            {
                "feature_id": str(test_data["reports"][0].feature_id),
                "report_model_id": str(test_data["report_models"][1].id),
                "custom_field_values": {"commentaire": "foo"},
            },
            headers={
                "Accept": "application/json",
                "sec-roles": "ROLE_USER",
                "sec-username": "bobby",
            },
        )
        assert r.json["updated_at"] == "2020-01-01T00:00:00+00:00"
        assert r.json["updated_by"] == "bobby"
        assert r.json["report_model_id"] == str(test_data["report_models"][1].id)

    def test_put_non_existing_record(self, test_app):
        r = test_app.put_json(
            f"/reports/{uuid4()}",
            {
                "feature_id": str(uuid4()),
                "report_model_id": str(uuid4()),
                "custom_field_values": {"unknown": "foo"},
            },
            headers={"sec-roles": "ROLE_USER", "Accept": "application/json"},
            status=404,
        )
        assert sorted(list(r.json.keys())) == sorted(["code", "message", "title"])
        assert r.json["code"] == "404 Not Found"
        assert r.json["title"] == "Not Found"
        assert r.json["message"].startswith("The resource could not be found")

    def test_put_update_pk(self, test_app, test_data):
        new_id = uuid4()
        r = test_app.put_json(
            f"/reports/{test_data['reports'][0].id}",
            {
                "id": str(new_id),
                "feature_id": str(test_data["reports"][0].feature_id),
                "report_model_id": str(test_data["report_models"][1].id),
                "custom_field_values": {"commentaire": "foo"},
            },
            headers={"sec-roles": "ROLE_USER", "Accept": "application/json"},
            status=200,
        )
        assert r.json["id"] == str(new_id)

    def test_delete_non_existing(self, test_app):
        r = test_app.delete(
            f"/reports/{uuid4()}",
            headers={"Accept": "application/json", "sec-roles": "ROLE_REPORTS_ADMIN"},
            status=404,
        )
        assert sorted(list(r.json.keys())) == sorted(["code", "message", "title"])
        assert r.json["code"] == "404 Not Found"
        assert r.json["title"] == "Not Found"
        assert r.json["message"].startswith("The resource could not be found")

    def test_unsufficient_permission(self, test_app):
        r = test_app.delete(
            f"/reports/{uuid4()}",
            headers={"Accept": "application/json", "sec-roles": "ROLE_USER"},
            status=403,
        )

        assert sorted(list(r.json.keys())) == sorted(["code", "message", "title"])
        assert r.json["code"] == "403 Forbidden"
        assert r.json["title"] == "Forbidden"
        assert r.json["message"].startswith("Access was denied to this resource.")

    def test_delete(self, test_app, test_data, dbsession):
        test_app.delete(
            f"/reports/{test_data['reports'][0].id}",
            headers={"sec-roles": "ROLE_REPORTS_ADMIN"},
            status=204,
        )
        assert (
            dbsession.query(Report)
            .filter(test_data["reports"][0].id == Report.id)
            .one_or_none()
            is None
        )
