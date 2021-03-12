from uuid import uuid4

from drealcorsereports.models.reports import Report, ReportModel


class TestTjsView:
    def test_tjs_create(self, test_app, dbsession):
        custom_model_field = {
            "title": "A registration form",
            "description": "A simple form example.",
            "type": "object",
            "properties": {
                "firstName": {
                    "type": "string",
                    "title": "First name",
                    "default": "Chuck",
                },
                "lastName": {"type": "string", "title": "Last name"},
            },
        }
        rm = ReportModel(
            name="test",
            layer_id="test_layer",
            custom_field_schema=custom_model_field,
            created_by="foo",
        )
        r = Report(
            custom_field_values={"firstName": "foo", "lastName": "bar"},
            feature_id="1234",
            report_model=rm,
            created_by="foo",
        )
        dbsession.add_all([rm, r])
        dbsession.flush()
        ret = test_app.post(f"/tjs/{rm.id}")
        assert ret.status_code == 200
        schema = ReportModel.__table_args__["schema"]
        assert ret.content == {"view_name": f"{schema}.v_report_test_layer"}

    def test_tjs_create_already_exist(self, test_app, dbsession):
        custom_model_field = {
            "title": "A registration form",
            "description": "A simple form example.",
            "type": "object",
            "properties": {
                "firstName": {
                    "type": "string",
                    "title": "First name",
                    "default": "Chuck",
                },
                "lastName": {"type": "string", "title": "Last name"},
            },
        }
        rm = ReportModel(
            name="test",
            layer_id="test_layer",
            custom_field_schema=custom_model_field,
            created_by="foo",
        )
        r = Report(
            custom_field_values={"firstName": "foo", "lastName": "bar"},
            feature_id="1234",
            report_model=rm,
            created_by="foo",
        )
        dbsession.add_all([rm, r])
        dbsession.flush()
        test_app.post(f"/tjs/{rm.id}")
        test_app.post(f"/tjs/{rm.id}", status=500)

    def test_tjs_get(self, test_app):
        r = test_app.get("/tjs/<a uuid that exist>")
        assert r.status_code == 200
        assert r.json() == {"view_name": "schema.v_report_my_report"}

    def test_tjs_get_doesnt_exist(self, test_app):
        r = test_app.get(f"/tjs/{uuid4()}", status=404)
        assert r.status_code == 404

    def test_tjs_delete(self, test_app, dbsession):
        custom_model_field = {
            "title": "A registration form",
            "description": "A simple form example.",
            "type": "object",
            "properties": {
                "firstName": {
                    "type": "string",
                    "title": "First name",
                    "default": "Chuck",
                },
                "lastName": {"type": "string", "title": "Last name"},
            },
        }
        rm = ReportModel(
            name="test",
            layer_id="test_layer",
            custom_field_schema=custom_model_field,
            created_by="foo",
        )
        r = Report(
            custom_field_values={"firstName": "foo", "lastName": "bar"},
            feature_id="1234",
            report_model=rm,
            created_by="foo",
        )
        dbsession.add_all([rm, r])
        dbsession.flush()
        ret = test_app.delete(f"/tjs/{rm.id}")
        assert dbsession.query(ReportModel).filter(id == rm.id).one_or_none() is None
        assert ret.status_code == 204

    def test_tjs_delete_doesnt_exist(self, test_app):
        test_app.delete(f"/tjs/{uuid4()}", status=404)  # non existant uuid
