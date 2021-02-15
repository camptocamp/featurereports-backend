from pyramid import testing
from pyramid.security import Everyone, Authenticated

from drealcorsereports.security import HeaderAuthentication


class TestHeaderAuthentication:
    def test_unauthenticated_userid(self):
        auth_policy = HeaderAuthentication()

        request = testing.DummyRequest()
        assert auth_policy.unauthenticated_userid(request) is None

        request.headers["sec-username"] = "test_user"
        assert auth_policy.unauthenticated_userid(request) == "test_user"

    def test_authenticated_userid(self):
        auth_policy = HeaderAuthentication()

        request = testing.DummyRequest()
        assert auth_policy.authenticated_userid(request) is None

        request.headers["sec-username"] = "test_user"
        assert auth_policy.authenticated_userid(request) == "test_user"

    def test_effective_principals(self):
        auth_policy = HeaderAuthentication()

        request = testing.DummyRequest()
        assert auth_policy.effective_principals(request) == [Everyone]

        request.headers["sec-username"] = "test_user"
        assert set(auth_policy.effective_principals(request)) == set(
            [Everyone, Authenticated, "test_user"]
        )

        request.headers["sec-roles"] = "role1;role2"
        assert set(auth_policy.effective_principals(request)) == set(
            [Everyone, Authenticated, "test_user", "role1", "role2"]
        )
