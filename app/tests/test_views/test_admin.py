from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import patch

import pytest
from drealcorsereports.models.reports import (
    FieldTypeEnum,
    ReportModel,
    ReportModelCustomField,
)
from pyramid.httpexceptions import HTTPBadRequest

USER_ADMIN = "USER_ADMIN"
ROLE_REPORTS_ADMIN = "ROLE_REPORTS_ADMIN"

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
                    name="commentaire",
                    type=FieldTypeEnum.string,
                )
            ],
        ),
        ReportModel(
            name="existing_denied",
            layer_id=DENIED_LAYER,
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
        ),
    ]
    dbsession.add_all(report_models)
    dbsession.flush()
    dbsession.expire_all()
    yield {
        "report_models": report_models,
    }


@pytest.fixture(scope="class")
def patch_is_user_admin_on_layer():
    def is_user_admin_on_layer(user_id, layer_id):
        del user_id
        return layer_id == ALLOWED_LAYER

    with patch(
        "drealcorsereports.views.admin.is_user_admin_on_layer",
        side_effect=is_user_admin_on_layer,
    ) as view_mock, patch(
        "drealcorsereports.schemas.reports.is_user_admin_on_layer",
        side_effect=is_user_admin_on_layer,
    ) as schema_mock:
        yield view_mock, schema_mock


@pytest.mark.usefixtures("transact", "patch_is_user_admin_on_layer")
class TestAdminReportModelView:
    def _auth_headers(self, username=USER_ADMIN, roles=[ROLE_REPORTS_ADMIN]):
        return {
            "sec-username": username,
            "sec-roles": ";".join(roles),
        }

    def test_collection_get_forbidden(self, test_app):
        test_app.get(
            "/report_models",
            headers=self._auth_headers(roles=[]),
            status=403,
        )

    def test_collection_get_success(self, test_app, test_data):
        r = test_app.get(
            "/report_models",
            headers=self._auth_headers(),
            status=200,
        )
        assert r.json == [
            {
                "id": str(test_data["report_models"][0].id),
                "name": "existing_allowed",
                "layer_id": ALLOWED_LAYER,
                "custom_fields": [
                    {
                        "enum": None,
                        "id": str(test_data["report_models"][0].custom_fields[0].id),
                        "index": 0,
                        "name": "commentaire",
                        "type": "string",
                        "required": False,
                    }
                ],
                "created_by": "toto",
                "created_at": "2021-01-22T13:33:00+00:00",
                "updated_by": "tata",
                "updated_at": "2021-01-22T13:34:00+00:00",
            },
            {
                "id": str(test_data["report_models"][1].id),
                "name": "existing_denied",
                "layer_id": DENIED_LAYER,
                "custom_fields": [
                    {
                        "enum": None,
                        "id": str(test_data["report_models"][1].custom_fields[0].id),
                        "index": 0,
                        "name": "commentaire",
                        "type": "string",
                        "required": False,
                    }
                ],
                "created_by": "toto",
                "created_at": "2021-01-22T13:33:00+00:00",
                "updated_by": "tata",
                "updated_at": "2021-01-22T13:34:00+00:00",
            },
        ]

    def test_collection_get_empty(self, test_app):
        r = test_app.get(
            "/report_models",
            headers=self._auth_headers(),
            status=200,
        )
        assert r.json == []

    def _post_payload(self, **kwargs):
        return {
            "name": "new",
            "layer_id": ALLOWED_LAYER,
            "custom_fields": [
                {
                    "name": "category",
                    "type": "string",
                    "enum": [
                        "category1",
                        "category2",
                    ],
                    "required": True,
                },
                {
                    "name": "commentaire",
                    "type": "string",
                    "required": False,
                },
            ],
            **kwargs,
        }

    def test_collection_post_forbidden(self, test_app):
        test_app.post_json(
            "/report_models",
            self._post_payload(),
            headers=self._auth_headers(roles=[]),
            status=403,
        )

    def test_collection_post_success(self, test_app, dbsession):
        r = test_app.post_json(
            "/report_models",
            self._post_payload(),
            headers=self._auth_headers(),
            status=201,
        )
        report_model = dbsession.query(ReportModel).get(r.json["id"])
        assert report_model.name == "new"
        assert len(report_model.custom_fields) == 2

        assert report_model.custom_fields[0].name == "category"
        assert report_model.custom_fields[0].index == 0
        assert report_model.custom_fields[0].type == FieldTypeEnum.string
        assert report_model.custom_fields[0].enum == [
            "category1",
            "category2",
        ]
        assert report_model.custom_fields[0].required == True

        assert report_model.custom_fields[1].name == "commentaire"
        assert report_model.custom_fields[1].index == 1
        assert report_model.custom_fields[1].type == FieldTypeEnum.string
        assert report_model.custom_fields[1].enum is None
        assert report_model.custom_fields[1].required == False

        assert report_model.layer_id == ALLOWED_LAYER
        assert report_model.created_by == USER_ADMIN
        assert isinstance(report_model.created_at, datetime)
        assert report_model.created_at.tzinfo is not None
        assert report_model.updated_by == USER_ADMIN
        assert isinstance(report_model.updated_at, datetime)
        assert report_model.updated_at.tzinfo is not None

    def test_collection_post_name_unique_validator(self, test_app, dbsession):
        r = test_app.post_json(
            "/report_models",
            self._post_payload(),
            headers=self._auth_headers(),
            status=201,
        )
        report_model = dbsession.query(ReportModel).get(r.json["id"])
        assert report_model.name == "new"

        r = test_app.post_json(
            "/report_models",
            self._post_payload(),
            headers=self._auth_headers(),
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

    def test_collection_post_not_layer_admin(self, test_app):
        r = test_app.post_json(
            "/report_models",
            self._post_payload(layer_id=DENIED_LAYER),
            headers=self._auth_headers(),
            status=400,
        )
        assert r.json == {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "layer_id",
                    "description": ["You're not admin on layer DENIED_LAYER."],
                }
            ],
        }

    def test_get_forbidden(self, test_app, test_data):
        rm = test_data["report_models"][0]
        test_app.get(
            f"/report_models/{rm.id}",
            headers=self._auth_headers(roles=[]),
            status=403,
        )

    def test_get_success(self, test_app, test_data):
        rm = test_data["report_models"][0]
        r = test_app.get(
            f"/report_models/{rm.id}",
            headers=self._auth_headers(),
            status=200,
        )
        assert r.json == {
            "id": str(rm.id),
            "name": "existing_allowed",
            "layer_id": ALLOWED_LAYER,
            "custom_fields": [
                {
                    "enum": None,
                    "id": str(rm.custom_fields[0].id),
                    "index": 0,
                    "name": "commentaire",
                    "type": "string",
                    "required": False,
                }
            ],
            "created_by": "toto",
            "created_at": "2021-01-22T13:33:00+00:00",
            "updated_by": "tata",
            "updated_at": "2021-01-22T13:34:00+00:00",
        }

    def test_get_not_found(self, test_app):
        test_app.get(
            f"/report_models/{uuid4()}",
            headers=self._auth_headers(),
            status=404,
        )

    def _put_payload(self, rm, **kwargs):
        return {
            "id": str(rm.id),
            "name": "updated",
            "layer_id": ALLOWED_LAYER,
            "custom_fields": [
                {
                    "id": str(rm.custom_fields[0].id),
                    "name": "commentaire_renamed",
                    "type": "string",
                },
                {
                    "name": "commentaire2",
                    "type": "string",
                },
            ],
            **kwargs,
        }

    def test_put_forbidden(self, test_app, test_data):
        # No admin role
        rm = test_data["report_models"][0]
        test_app.put_json(
            f"/report_models/{rm.id}",
            self._put_payload(rm),
            headers=self._auth_headers(roles=[]),
            status=403,
        )

        # Not admin on actual layer
        rm = test_data["report_models"][1]
        test_app.put_json(
            f"/report_models/{rm.id}",
            self._put_payload(rm),
            headers=self._auth_headers(),
            status=403,
        )

    def test_put_success(self, test_app, test_data):
        rm = test_data["report_models"][0]
        updated_at = rm.updated_at
        r = test_app.put_json(
            f"/report_models/{rm.id}",
            self._put_payload(rm),
            headers=self._auth_headers(username="ANOTHER_USER"),
            status=200,
        )
        assert r.json["id"] == str(rm.id)
        assert rm.name == "updated"
        assert rm.layer_id == ALLOWED_LAYER
        assert len(rm.custom_fields) == 2
        assert rm.custom_fields[0].name == "commentaire_renamed"
        assert rm.custom_fields[0].index == 0
        assert rm.custom_fields[1].name == "commentaire2"
        assert rm.custom_fields[1].index == 1
        assert rm.updated_by == "ANOTHER_USER"
        assert rm.updated_at != updated_at

    def test_put_not_layer_admin(self, test_app, test_data):
        rm = test_data["report_models"][0]
        r = test_app.put_json(
            f"/report_models/{rm.id}",
            self._put_payload(rm, layer_id=DENIED_LAYER),
            headers=self._auth_headers(),
            status=400,
        )
        assert r.json == {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "layer_id",
                    "description": ["You're not admin on layer DENIED_LAYER."],
                }
            ],
        }

    def test_put_not_found(self, test_app):
        test_app.put_json(
            f"/report_models/{uuid4()}",
            {},
            headers=self._auth_headers(),
            status=404,
        )

    def test_delete_forbidden(self, test_app, test_data):
        # No admin role
        rm = test_data["report_models"][0]
        test_app.delete(
            f"/report_models/{rm.id}",
            headers=self._auth_headers(roles=[]),
            status=403,
        )

        # Not admin on actual layer
        rm = test_data["report_models"][1]
        test_app.delete(
            f"/report_models/{rm.id}",
            headers=self._auth_headers(),
            status=403,
        )

    def test_delete_success(self, test_app, dbsession, test_data):
        rm = test_data["report_models"][0]
        test_app.delete(
            f"/report_models/{rm.id}",
            headers=self._auth_headers(),
            status=204,
        )
        dbsession.flush()
        assert dbsession.query(ReportModel).get(rm.id) is None

    def test_delete_not_found(self, test_app):
        test_app.delete(
            f"/report_models/{uuid4()}",
            headers=self._auth_headers(),
            status=404,
        )
