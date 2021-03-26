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
def patch_is_user_anything_on_layer():
    def is_user_anything_on_layer(user_id, layer_id):
        del user_id
        return layer_id == ALLOWED_LAYER

    with patch(
        "drealcorsereports.views.report.is_user_admin_on_layer",
        side_effect=is_user_anything_on_layer,
    ) as admin_mock, patch(
        "drealcorsereports.views.report.is_user_writer_on_layer",
        side_effect=is_user_anything_on_layer,
    ) as write_mock, patch(
        "drealcorsereports.views.report.is_user_reader_on_layer",
        side_effect=is_user_anything_on_layer,
    ) as read_mock:
        yield admin_mock, write_mock, read_mock


@pytest.fixture
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
        layer_id=ALLOWED_LAYER,
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
        feature_id=uuid4(),
        report_model=rm1,
        custom_field_values={"commentaire": "foo"},
        created_by="foo",
        created_at=datetime.now(),
        updated_by="foo",
        updated_at=datetime.now(),
    )
    r2 = Report(
        feature_id=uuid4(),
        report_model=rm2,
        custom_field_values={"commentaire": "bar"},
        created_by="bar",
        created_at=datetime.now(),
        updated_by="bar",
        updated_at=datetime.now(),
    )
    r3 = Report(
        feature_id=uuid4(),
        report_model=rm2,
        custom_field_values={"something": "foo"},
        created_by="foo",
        created_at=datetime.now(),
        updated_by="foo",
        updated_at=datetime.now(),
    )
    r4 = Report(
        feature_id=uuid4(),
        report_model=rm2,
        custom_field_values={"something": "foo"},
        created_by="bar",
        created_at=datetime.now(),
        updated_by="bar",
        updated_at=datetime.now(),
    )
    dbsession.add_all([r1, r2, r3, r4])
    dbsession.flush()
    dbsession.expire_all()
    yield {"report_models": [rm1, rm2], "reports": [r1, r2, r3, r4]}


@pytest.mark.usefixtures("patch_is_user_anything_on_layer")
class TestReportView:
    # def test_collection_get_success(self, test_app, test_data):
    #     r = test_app.get("/reports", headers={"sec-roles": "ROLE_USER"})
    #     assert isinstance(r.json, list)
    #     assert len(r.json) == 4

    def test_collection_post_forbidden(self, test_app, test_data):
        r = test_app.post_json(
            "/reports",
            {
                "feature_id": str(uuid4()),
                "report_model_id": str(test_data["report_models"][0].id),
                "custom_field_values": {"commentaire": "foo"},
            },
            status=403,
            headers={"Accept": "application/json"},
        )
        assert sorted(list(r.json.keys())) == sorted(["code", "message", "title"])
        assert r.json["code"] == "403 Forbidden"
        assert r.json["title"] == "Forbidden"
        assert r.json["message"].startswith("Access was denied to this resource.")

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

    def test_collection_post_wrong_custom_fields(self, test_app, test_data):
        """
        FIXME This should fail.
        """
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
            status=201,
        )
        assert sorted(list(r.json.keys())) == sorted(
            [
                "id",
                "feature_id",
                "report_model_id",
                "custom_field_values",
                "created_by",
                "created_at",
                "updated_by",
                "updated_at",
            ]
        )
        assert r.json["feature_id"] == str(f_id)

    def test_get_success(self, test_app, test_data):
        r = test_app.get(
            f"/reports/{test_data['reports'][0].id}", headers={"sec-roles": "ROLE_USER"}
        )
        assert r.json["id"] == str(test_data["reports"][0].id)
        assert r.json["report_model_id"] == str(test_data["reports"][0].report_model_id)
        assert sorted(list(r.json.keys())) == sorted(
            [
                "id",
                "feature_id",
                "report_model_id",
                "custom_field_values",
                "created_by",
                "created_at",
                "updated_by",
                "updated_at",
            ]
        )

    def test_get_not_found(self, test_app):
        r = test_app.get(
            f"/reports/{uuid4()}",
            headers={"sec-roles": "ROLE_USER", "Accept": "application/json"},
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
