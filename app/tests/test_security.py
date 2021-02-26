from unittest import mock
from unittest.mock import PropertyMock

import pytest
from pyramid import testing
from pyramid.security import Everyone, Authenticated
import responses

from drealcorsereports.security import (
    HeaderAuthentication,
    is_user_admin_on_layer,
    Rule,
    RuleAccess,
)
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
        assert set(auth_policy.effective_principals(request)) == {
            Everyone,
            Authenticated,
            "test_user",
        }

        request.headers["sec-roles"] = "role1;role2"
        assert set(auth_policy.effective_principals(request)) == {
            Everyone,
            Authenticated,
            "test_user",
            "role1",
            "role2",
        }


class TestRules:
    def test_parse_read_wildcard(self):
        r = Rule.parse("*.*.r", "*")
        assert r.layer == "*"
        assert r.geoserver_roles == [
            "*",
        ]
        assert r.workspace == "*"
        assert r.rule_access == RuleAccess.READ

    def test_parse_write_workspace(self):
        r = Rule.parse("foo.*.w", "ADMIN")
        assert r.layer == "*"
        assert r.geoserver_roles == [
            "ADMIN",
        ]
        assert r.workspace == "foo"
        assert r.rule_access == RuleAccess.WRITE

    def test_parse_roles(self):
        r = Rule.parse("foo.bar.r", "ADMIN,ROLE_FOO")
        assert r.layer == "bar"
        assert r.geoserver_roles == ["ADMIN", "ROLE_FOO"]
        assert r.workspace == "foo"
        assert r.rule_access == RuleAccess.READ


class TestIsUserAdminOnLayer:
    @responses.activate
    def test_raise_on_not_found(self):
        request = testing.DummyRequest()
        request.registry.settings = {"geoserver_url": "https://toto/geoserver"}
        responses.add(
            responses.GET,
            "https://toto/geoserver/rest/security/acl/layers.json",
            status=404,
        )
        with pytest.raises(HTTPError) as e:
            is_user_admin_on_layer(request, "foo")
            assert (
                str(e.value)
                == "Not Found for url: https://toto/geoserver/rest/security/acl/layers.json"
            )

    @responses.activate
    def test_geoserver_admin_wildcard(self):
        with mock.patch(
            "pyramid.testing.DummyRequest.effective_principals",
            new_callable=PropertyMock,
        ) as mock_effective_principals:
            request = testing.DummyRequest()
            mock_effective_principals.return_value = ["ADMIN", "TOTO"]
            request.registry.settings = {"geoserver_url": "https://toto/geoserver"}
            responses.add(
                responses.GET,
                "https://toto/geoserver/rest/security/acl/layers.json",
                json={"*.*.a": "*"},
            )
            ret = is_user_admin_on_layer(request, "foo")
            assert ret is True

    @responses.activate
    def test_geoserver_not_admin_wildcard(self):
        with mock.patch(
            "pyramid.testing.DummyRequest.effective_principals",
            new_callable=PropertyMock,
        ) as mock_effective_principals:
            request = testing.DummyRequest()
            mock_effective_principals.return_value = ["ADMIN", "TOTO"]
            request.registry.settings = {"geoserver_url": "https://toto/geoserver"}
            responses.add(
                responses.GET,
                "https://toto/geoserver/rest/security/acl/layers.json",
                json={"*.foo.r": "ADMIN"},
            )
            ret = is_user_admin_on_layer(request, "foo")
            assert ret is False

    @responses.activate
    def test_geoserver_wrong_roles(self):
        with mock.patch(
            "pyramid.testing.DummyRequest.effective_principals",
            new_callable=PropertyMock,
        ) as mock_effective_principals:
            request = testing.DummyRequest()
            mock_effective_principals.return_value = ["ADMIN", "TOTO"]
            request.registry.settings = {"geoserver_url": "https://toto/geoserver"}
            responses.add(
                responses.GET,
                "https://toto/geoserver/rest/security/acl/layers.json",
                json={"*.foo.r": "ADMIN", "bar.baz.a": "NOT_YOU"},
            )
            ret = is_user_admin_on_layer(request, "foo")
            assert ret is False
