from datetime import datetime, timezone
from uuid import UUID

from cornice.resource import resource, view
from cornice.validators import marshmallow_body_validator
from pyramid.exceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.security import Allow, Everyone

from drealcorsereports.models.reports import Report, ReportModel
from drealcorsereports.schemas.reports import ReportSchema
from drealcorsereports.security import (
    is_user_reader_on_layer,
    is_user_writer_on_layer,
)


def marshmallow_validator(request: Request, **kwargs):
    return marshmallow_body_validator(
        request,
        schema=kwargs.get("schema"),
        schema_kwargs={"session": request.dbsession},
    )


def layer_id_validator(request, **kwargs):
    del kwargs
    if "layer_id" not in request.params:
        request.errors.add("querystring", "layer_id", "You need to provide a layer_id")
    else:
        request.layer_id = request.params["layer_id"]


def feature_id_validator(request, **kwargs):
    del kwargs
    if "feature_id" not in request.params:
        request.errors.add(
            "querystring", "feature_id", "You need to provide a feature_id"
        )
    else:
        request.feature_id = request.params["feature_id"]


@resource(
    collection_path="/reports",
    path="/reports/{id}",
    cors_origins=("*",),
)
class ReportView:
    def __init__(self, request: Request, context=None) -> None:
        self.request = request
        del context
        if self.request.matchdict.get("id"):
            self.report_id = UUID(self.request.matchdict.get("id"))

    def __acl__(self):
        """
        User with role ROLE_REPORTS_ADMIN have the right to do anything.
        For a specific user, we check geoserver rules.
        """
        acl = [
            (Allow, "ROLE_REPORTS_ADMIN", ("list", "add", "view", "delete")),
        ]

        # In case of list we get layer_id from request params
        if "layer_id" in self.request.params:
            layer_id = self.request.params["layer_id"]
            if is_user_reader_on_layer(self.request, layer_id):
                acl.append((Allow, self.request.authenticated_userid, "list"))

        elif self.request.method == "POST":
            # We give everyone the add permission and returns validation error if needed
            acl.append((Allow, Everyone, "add"))

        else:
            # Other permissions are based on existing object
            layer_id = self._get_object().report_model.layer_id
            if is_user_reader_on_layer(self.request, layer_id):
                acl.append((Allow, self.request.authenticated_userid, "view"))
            if is_user_writer_on_layer(self.request, layer_id):
                acl.append(
                    (Allow, self.request.authenticated_userid, ("edit", "delete"))
                )

        return acl

    @view(permission="list", validators=[layer_id_validator, feature_id_validator])
    def collection_get(self) -> list:
        session = self.request.dbsession
        reports = (
            session.query(Report)
            .join(ReportModel)
            .filter(ReportModel.layer_id == self.request.layer_id)
            .filter(Report.feature_id == self.request.feature_id)
        )
        report_schema = ReportSchema()
        return [report_schema.dumps(r) for r in reports]

    @view(permission="add", schema=ReportSchema, validators=(marshmallow_validator,))
    def collection_post(self):
        report = self.request.validated
        report.created_by = self.request.authenticated_userid
        report.updated_by = self.request.authenticated_userid
        self.request.dbsession.add(report)
        self.request.dbsession.flush()
        self.request.response.status_code = 201
        self.request.response.content_location = f"reports/{report.id}"
        return ReportSchema().dump(report)

    def _get_object(self) -> Report:
        session = self.request.dbsession
        r = session.query(Report).get(self.report_id)
        if r is None:
            raise HTTPNotFound()
        return r

    @view(permission="view")
    def get(self) -> dict:
        return ReportSchema().dump(self._get_object())

    @view(permission="edit", schema=ReportSchema, validators=(marshmallow_validator,))
    def put(self) -> dict:
        # generate 404 if the report doesn't exists.
        self._get_object()
        report = self.request.validated
        report.updated_by = self.request.authenticated_userid
        report.updated_at = datetime.now(timezone.utc)
        return ReportSchema().dump(report)

    @view(permission="delete")
    def delete(self) -> None:
        self.request.dbsession.delete(self._get_object())
        self.request.response.status_code = 204
