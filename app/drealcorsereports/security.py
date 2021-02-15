from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.request import Request
from pyramid.security import Authenticated, Everyone
from zope.interface import implementer


def is_user_admin_on_layer(request: Request, layer_id: str):
    "Return True if user is admin on considered layer"
    # TODO: request GeoServer
    del request
    del layer_id
    return True


@implementer(IAuthenticationPolicy)
class HeaderAuthentication:
    def unauthenticated_userid(self, request):
        return request.headers.get("sec-username", None)

    def authenticated_userid(self, request):
        return self.unauthenticated_userid(request)

    def effective_principals(self, request):
        effective_principals = [Everyone]

        userid = self.authenticated_userid(request)
        if userid is not None:
            effective_principals += [Authenticated, str(userid)]

        roles = request.headers.get("sec-roles", "")
        if roles != "":
            effective_principals += [r.strip() for r in roles.split(";")]

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
