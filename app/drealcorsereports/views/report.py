from datetime import datetime, timezone
from uuid import UUID

from cornice.resource import resource, view
from cornice.validators import marshmallow_body_validator
from pyramid.request import Request
from pyramid.exceptions import HTTPNotFound

from drealcorsereports.models.reports import Report
from drealcorsereports.schemas.reports import ReportSchema
from pyramid.security import Allow


def marshmallow_validator(request: Request, **kwargs):
    return marshmallow_body_validator(
        request,
        schema=kwargs.get("schema"),
        schema_kwargs={"session": request.dbsession},
    )


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
        acl = [
            (Allow, "ROLE_USER", ("list", "add")),
            (Allow, "ROLE_REPORTS_ADMIN", ("list", "add", "view", "delete")),
        ]
        return acl

    @view(permission="list")
    def collection_get(self) -> list:
        session = self.request.dbsession
        reports = session.query(Report)
        report_schema = ReportSchema()
        return [report_schema.dumps(r) for r in reports]

    @view(schema=ReportSchema, validators=(marshmallow_validator,), permission="add")
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

    @view(permission="list")
    def get(self) -> dict:
        return ReportSchema().dump(self._get_object())

    @view(schema=ReportSchema, validators=(marshmallow_validator,), permission="add")
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
