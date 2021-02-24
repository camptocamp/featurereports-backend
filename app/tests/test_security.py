import pytest
from pyramid import testing
from pyramid.security import Everyone, Authenticated
import responses

from drealcorsereports.security import HeaderAuthentication, is_user_admin_on_layer, Rule, RuleAccess
from requests import HTTPError


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
        assert set(auth_policy.effective_principals(request)) == {Everyone, Authenticated, "test_user"}

        request.headers["sec-roles"] = "role1;role2"
        assert set(auth_policy.effective_principals(request)) == {Everyone, Authenticated, "test_user", "role1",
                                                                  "role2"}


class TestRules:
    def test_parse_read_wildcard(self):
        r = Rule.parse("*.*.r", "*")
        assert r.layer == '*'
        assert r.roles == ['*',]
        assert r.workspace == '*'
        assert r.rule_access == RuleAccess.READ

    def test_parse_write_workspace(self):
        r = Rule.parse("foo.*.w", "ADMIN")
        assert r.layer == '*'
        assert r.roles == ['ADMIN',]
        assert r.workspace == 'foo'
        assert r.rule_access == RuleAccess.WRITE

    def test_parse_roles(self):
        r = Rule.parse("foo.bar.r", "ADMIN,ROLE_FOO")
        assert r.layer == 'bar'
        assert r.roles == ['ADMIN', 'ROLE_FOO']
        assert r.workspace == 'foo'
        assert r.rule_access == RuleAccess.READ

class TestIsUserAdminOnLayer:
    @responses.activate
    def test_raise_on_not_found(self):
        request = testing.DummyRequest()
        request.registry.settings = {
            'geoserver_url': 'https://toto/geoserver'
        }
        responses.add(responses.GET, 'https://toto/geoserver/rest/security/acl/layers.json', status=404)
        with pytest.raises(HTTPError) as e:
            is_user_admin_on_layer(request, 'foo')
            assert str(e.value) == 'Not Found for url: https://toto/geoserver/rest/security/acl/layers.json'


    @responses.activate
    def test_geoserver_admin_wildcard(self):
        request = testing.DummyRequest()
        request.registry.settings = {
            'geoserver_url': 'https://toto/geoserver'
        }
        responses.add(responses.GET, 'https://toto/geoserver/rest/security/acl/layers.json', json={"*.*.a": "*"})
        ret = is_user_admin_on_layer(request, 'foo')
        assert ret is True

