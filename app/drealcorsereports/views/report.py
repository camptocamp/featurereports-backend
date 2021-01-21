from pyramid.request import Request
from cornice.resource import resource, view
from drealcorsereports.models.reports import Report
from drealcorsereports.schemas.reports import ReportSchema
from uuid import UUID
from pyramid.exceptions import HTTPNotFound
from cornice.validators import marshmallow_body_validator


def marshmallow_validator(request: Request, **kwargs):
    return marshmallow_body_validator(
        request,
        schema_kwargs={"session": request.dbsession},
        schema=kwargs.get("schema"),
    )


def marshmallow_errors(request: Request) -> list:
    return request.errors


@resource(
    collection_path="/reports",
    path="/reports/{id}",
    renderer="json",
    cors_origins=("*",),
    error_handler=marshmallow_errors,
)
class ReportView:
    def __init__(self, request: Request, context=None) -> None:
        self.request = request
        if self.request.matchdict.get("id"):
            self.report_id = UUID(self.request.matchdict.get("id"))

    def collection_get(self) -> list:
        session = self.request.dbsession
        reports = session.query(Report)
        report_schema = ReportSchema()
        return [report_schema.dumps(r) for r in reports]

    @view(schema=ReportSchema, validators=(marshmallow_validator,))
    def collection_post(self):
        x = self.request.validated

    def get(self) -> str:
        session = self.request.dbsession
        r = session.query(Report).filter(Report.id == self.report_id).one_or_none()
        if r:
            return ReportSchema().dumps(r)
        else:
            raise HTTPNotFound()

    def patch(self) -> None:
        pass

    def delete(self) -> None:
        session = self.request.dbsession
        session.query(Report).filter(Report.id == self.report_id).delete()
        self.request.response.status_code = 204
