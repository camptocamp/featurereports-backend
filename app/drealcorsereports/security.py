from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import Authenticated, Everyone
from zope.interface import implementer


@implementer(IAuthenticationPolicy)
class HeaderAuthentication:
    def unauthenticated_userid(self, request):
        return request.headers.get("sec-username", None)

    def authenticated_userid(self, request):
        return self.unauthenticated_userid(request)

    def effective_principals(self, request):
        effective_principals = [Everyone]
        if self.authenticated_userid(request) is not None:
            effective_principals.append(Authenticated)
        return effective_principals

    def remember(self, request, userid, **kw):  # pylint: disable=unused-argument
        """A no-op."""
        return []

    def forget(self, request):  # pylint: disable=unused-argument
        """A no-op."""
        return []


def includeme(config):
    config.set_authentication_policy(HeaderAuthentication())
    config.set_authorization_policy(ACLAuthorizationPolicy())