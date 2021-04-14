from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

import pytest
from drealcorsereports.models.reports import ReportModel, ReportModelCustomField, FieldTypeEnum, Report
from sqlalchemy import text

ALLOWED_LAYER = "allowed_layer"

@pytest.fixture
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

class TestTjsView:
    def test_report_doesnt_exist(self, test_app):
        test_app.post(f"/tjs/reports/{uuid4()}", status=404)

    def test_wrong_permission(self):
        pass

    @pytest.mark.usefixtures("patch_check_user_right")
    def test_create_view(self, test_app, dbsession):
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
        dbsession.add(rm1)
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
            report_model=rm1,
            custom_field_values={"commentaire": "bar"},
            created_by="bar",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="bar",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
        )
        dbsession.add_all([r1, r2])
        dbsession.flush()

        ret = test_app.post(f"/tjs/reports/{rm1.id}")
        assert ret.json == {"view": f"{rm1.__table_args__['schema']}.v_tjs_view_{rm1.name}"}
        db_res = dbsession.execute(text(f"SELECT * FROM {ret.json['view']}"))
        assert [r.commentaire for r in db_res] == ["foo", "bar"]
