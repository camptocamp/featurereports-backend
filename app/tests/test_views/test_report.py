class TestReportView:
    def test_get_none(self, test_app):
        r = test_app.get("/reports")
        assert r.status_code == 200
        assert r.json == []
