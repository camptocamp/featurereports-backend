

class TestHello:

    def test_get_info(self, test_app):
        test_app.get('/', status=200)
