from datetime import datetime, timezone
from uuid import UUID

from cornice.resource import resource, view
from cornice.validators import marshmallow_body_validator
from pyramid.request import Request
from pyramid.httpexceptions import HTTPNotFound, HTTPUnprocessableEntity

from drealcorsereports.models.reports import Report
from drealcorsereports.schemas.reports import ReportSchema


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
            try:
                self.report_id = UUID(self.request.matchdict.get("id"))
            except ValueError:
                self.request.errors.add("body", "id", "Your id seems malformed")
                self.request.errors.status = 422
                return

    def collection_get(self) -> list:
        session = self.request.dbsession
        reports = session.query(Report)
        report_schema = ReportSchema()
        return [report_schema.dumps(r) for r in reports]

    @view(schema=ReportSchema, validators=(marshmallow_validator,))
    def collection_post(self):
        report = self.request.validated
        # TODO need to extract user from header properly
        report.created_by = self.request.headers.get("sec-username", "toto")
        self.request.dbsession.add(report)
        self.request.response.status_code = 201
        self.request.response.location = f"/admin/reports/{report.id}"
        return {"id": report.id}

    def _get_object(self) -> Report:
        session = self.request.dbsession
        rm = session.query(Report).get(self.report_id)
        if rm is None:
            raise HTTPNotFound()
        return rm

    def get(self) -> str:
        return ReportSchema().dump(self._get_object())

    def put(self) -> None:
        report = self.request.validated
        report.updated_by = self.request.headers["sec-username"]
        report.updated_at = datetime.now(timezone.utc)
        return ReportSchema().dump(report)

    def delete(self) -> None:
        self.request.dbsession.delete(self._get_object())
        self.request.response.status_code = 204
