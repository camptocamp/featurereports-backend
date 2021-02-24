"""
Admin rest services.
"""
from datetime import datetime, timezone
from uuid import UUID

from cornice.resource import resource, view
from cornice.validators import marshmallow_body_validator
from pyramid.exceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.security import Allow

from drealcorsereports.models.reports import ReportModel
from drealcorsereports.schemas.reports import ReportModelSchema
from drealcorsereports.security import is_user_admin_on_layer


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
        acl = [
            (Allow, "ROLE_REPORTS_ADMIN", ("list", "add", "view")),
            (Allow, "ROLE_SUPERUSER", ("list", "add", "view", "edit", "delete")),
        ]
        if (
            self.report_models_id
            and "ROLE_REPORTS_ADMIN" in self.request.effective_principals
        ):
            if is_user_admin_on_layer(self.request, self._get_object().layer_id):
                acl.extend(
                    [
                        (Allow, self.request.authenticated_userid, ("edit", "delete")),
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
        self.request.response.status_code = 201
        return ReportModelSchema().dump(report_model)

    def _get_object(self) -> ReportModel:
        session = self.request.dbsession
        rm = session.query(ReportModel).get(self.report_models_id)
        if rm is None:
            raise HTTPNotFound()
        return rm

    @view(permission="view")
    def get(self) -> dict:
        return ReportModelSchema().dump(self._get_object())

    @view(
        permission="edit", schema=ReportModelSchema, validators=(marshmallow_validator,)
    )
    def put(self) -> dict:
        self._get_object()
        report_model = self.request.validated
        report_model.updated_by = self.request.authenticated_userid
        report_model.updated_at = datetime.now(timezone.utc)
        return ReportModelSchema().dump(report_model)

    @view(permission="delete")
    def delete(self) -> None:
        self.request.dbsession.delete(self._get_object())
        self.request.response.status_code = 204
