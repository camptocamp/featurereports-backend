"""
Admin rest services.
"""
from datetime import datetime, timezone
from typing import List
from uuid import UUID

import requests
from cornice import Service
from cornice.resource import resource, view
from cornice.validators import marshmallow_body_validator
from pyramid.exceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.security import Allow, Authenticated

from drealcorsereports.models.reports import ReportModel
from drealcorsereports.schemas.reports import ReportModelSchema
from drealcorsereports.security import (
    is_user_admin_on_layer,
    get_geoserver_layers_acl,
    Rule,
)


def marshmallow_validator(request: Request, **kwargs):
    return marshmallow_body_validator(
        request,
        schema=kwargs.get("schema"),
        schema_kwargs={"session": request.dbsession},
    )


@resource(
    collection_path="/report_models",
    path="/report_models/{id}",
    cors_origins=("*",),
)
class AdminReportModelView:
    def __init__(self, request: Request, context=None) -> None:
        self.request = request
        self.context = context
        if self.request.matchdict.get("id"):
            self.report_models_id = UUID(self.request.matchdict.get("id"))
        else:
            self.report_models_id = None

    def __acl__(self):
        """
        User with role ROLE_REPORTS_ADMIN have the right to do anything.
        For a specific user, we check geoserver rules.
        """
        acl = [
            (Allow, "ROLE_REPORTS_ADMIN", ("list", "add", "view", "edit", "delete")),
            (Allow, "ROLE_SUPERUSER", ("list", "add", "view", "edit", "delete")),
            (Allow, Authenticated, ("list", "add")),
            # We give all authenticated users the add permission but returns validation error if needed
        ]
        if self.report_models_id:
            if is_user_admin_on_layer(self.request, self.get_object().layer_id):
                acl.extend(
                    [
                        (
                            Allow,
                            self.request.authenticated_userid,
                            ("view", "edit", "delete"),
                        ),
                    ]
                )
        return acl

    @view(permission="list")
    def collection_get(self) -> list:
        session = self.request.dbsession
        rms = session.query(ReportModel)
        report_model_schema = ReportModelSchema()
        return [report_model_schema.dump(rm) for rm in rms]

    @view(
        permission="add", schema=ReportModelSchema, validators=(marshmallow_validator,)
    )
    def collection_post(self) -> dict:
        report_model = self.request.validated
        # TODO need to extract user from header properly
        report_model.created_by = self.request.authenticated_userid
        report_model.updated_by = self.request.authenticated_userid
        self.request.dbsession.add(report_model)
        self.request.dbsession.flush()
        report_model.create_tjs_view()
        self.request.response.status_code = 201
        return ReportModelSchema().dump(report_model)

    def get_object(self) -> ReportModel:
        session = self.request.dbsession
        rm = session.query(ReportModel).get(self.report_models_id)
        if rm is None:
            raise HTTPNotFound()
        return rm

    @view(permission="view")
    def get(self) -> dict:
        return ReportModelSchema().dump(self.get_object())

    @view(
        permission="edit", schema=ReportModelSchema, validators=(marshmallow_validator,)
    )
    def put(self) -> dict:
        self.get_object()
        report_model = self.request.validated
        report_model.updated_by = self.request.authenticated_userid
        report_model.updated_at = datetime.now(timezone.utc)
        self.request.dbsession.flush()
        report_model.update_tjs_view()
        return ReportModelSchema().dump(report_model)

    @view(permission="delete")
    def delete(self) -> None:
        report_model = self.get_object()
        self.request.dbsession.delete(report_model)
        report_model.drop_tjs_view()
        self.request.response.status_code = 204


list_layers = Service(
    name="list_layers",
    path="/layers",
    description="list of layers from geoserver based on right you have.",
)


@list_layers.get()
def get_layers(request: Request) -> List:
    layers_request = requests.get(
        request.registry.settings.get("geoserver_url") + "/rest/layers.json",
        headers={
            "Sec-Username": "geoserver_privileged_user",
            "Sec-Roles": "ROLE_ADMINISTRATOR",
        },
    )
    layers_request.raise_for_status()
    layers = layers_request.json()
    layer_rules_json = get_geoserver_layers_acl(
        request.registry.settings.get("geoserver_url")
    )
    authorized_layers = list()
    for layer in layers["layers"]["layer"]:
        for layer_rules in layer_rules_json.items():
            rule = Rule.parse(*layer_rules)
            if rule.match(layer["name"], request.effective_principals):
                authorized_layers.append(layer["name"])

    return authorized_layers
