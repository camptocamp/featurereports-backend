from enum import Enum
from typing import List, Tuple, Dict

import requests
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.request import Request
from pyramid.security import Authenticated, Everyone
from zope.interface import implementer


class RuleAccess(Enum):
    READ = "r"
    WRITE = "w"
    ADMIN = "a"


class Rule:
    def __init__(
        self,
        workspace: str,
        layer: str,
        rule_access: RuleAccess,
        geoserver_roles: List[str],
    ):
        self.workspace = workspace
        self.layer = layer
        self.rule_access = rule_access
        self.geoserver_roles = geoserver_roles

    @staticmethod
    def parse(*geoserver_rule) -> "Rule":
        workspace, layer, access = geoserver_rule[0].split(".")
        roles = geoserver_rule[1].split(",")
        return Rule(workspace, layer, RuleAccess(access), roles)

    def match(
        self,
        layer_id: str,
        roles: set,
        required_rule_access: RuleAccess = RuleAccess.ADMIN,
    ) -> bool:
        # List all rules that need to be satisfied.
        workspace, layer = self._parse_layer_id(layer_id)
        predicates = (
            self.workspace == workspace or self.workspace == "*",
            self.layer == layer or self.layer == "*",
            set(roles).intersection(self.geoserver_roles)
            or "*" in self.geoserver_roles,
            self.rule_access == required_rule_access,
        )
        if all(predicates):
            return True
        return False

    def _parse_layer_id(self, layer_id: str) -> Tuple[str, str]:
        splited_layer_name = layer_id.split(":")
        if len(splited_layer_name) == 1:
            return None, splited_layer_name[0]  # type: ignore
        if len(splited_layer_name) > 2:
            raise AssertionError(
                f"Layer name is not formated properly, accepted format 'workspace:layer' or 'layer' found '{layer_id}'"
            )
        return splited_layer_name  # type: ignore


def get_geoserver_layers_acl(geoserver_url: str) -> Dict:
    layer_rules_response = requests.get(
        f"{geoserver_url}/rest/security/acl/layers.json",
        headers={
            "sec-roles": "ROLE_ADMINISTRATOR",
            "sec-username": "geoserver_privileged_user",
        },
    )
    layer_rules_response.raise_for_status()
    return layer_rules_response.json()


def geoserver_rules(request) -> List[Rule]:
    layer_rules_json = get_geoserver_layers_acl(
        request.registry.settings.get("geoserver_url")
    )
    rules = []
    for kv in layer_rules_json.items():
        rules.append(Rule.parse(*kv))
    return rules


def check_user_right(
    request: Request, layer_id: str, level_required: RuleAccess
) -> bool:
    for rule in request.geoserver_rules:
        if rule.match(layer_id, request.effective_principals, level_required):
            return True
    return False


def is_user_reader_on_layer(request: Request, layer_id: str) -> bool:
    """
    Return True if user can read data from considered layer
    """
    return check_user_right(request, layer_id, RuleAccess.READ) or check_user_right(
        request, layer_id, RuleAccess.ADMIN
    )


def is_user_writer_on_layer(request: Request, layer_id: str) -> bool:
    """
    Return True if user can write data to considered layer
    """
    return check_user_right(request, layer_id, RuleAccess.WRITE) or check_user_right(
        request, layer_id, RuleAccess.ADMIN
    )


def is_user_admin_on_layer(request: Request, layer_id: str) -> bool:
    """
    Return True if user can access and modify configuration of considered layer
    """
    return check_user_right(request, layer_id, RuleAccess.ADMIN)


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
    config.add_request_method(geoserver_rules, "geoserver_rules", reify=True)
