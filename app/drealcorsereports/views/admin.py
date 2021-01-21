"""
Admin rest services.
"""
from uuid import UUID
from cornice.resource import resource, view
from pyramid.request import Request
from cornice.validators import marshmallow_body_validator
from drealcorsereports.models.reports import ReportModel
from drealcorsereports.schemas.reports import ReportModelSchema
from pyramid.exceptions import HTTPNotFound, HTTPBadRequest


def marshmallow_validator(request: Request, **kwargs):
    return marshmallow_body_validator(
        request,
        schema_kwargs={"session": request.dbsession},
        schema=kwargs.get("schema"),
    )


def marshmallow_errors(request: Request) -> list:
    return request.errors


@resource(
    collection_path="/admin/report_models",
    path="/admin/report_models/{id}",
    renderer="json",
    cors_origins=("*",),
    error_handler=marshmallow_errors,
)
class AdminReportModelView:
    def __init__(self, request: Request, context=None) -> None:
        self.request = request
        self.context = context
        if self.request.matchdict.get("id"):
            self.report_models_id = UUID(self.request.matchdict.get("id"))

    def collection_get(self) -> list:
        session = self.request.dbsession
        rms = session.query(ReportModel)
        report_model_schema = ReportModelSchema()
        return [report_model_schema.dump(rm) for rm in rms]

    @view(schema=ReportModelSchema, validators=(marshmallow_validator,))
    def collection_post(self):
        try:
            report_model = self.request.validated
            #TODO need to extract user from header properly
            report_model.created_by = self.request.headers.get('sec-username', "toto")
            self.request.dbsession.add(report_model)
            self.request.response.status_code = 201
            self.request.response.location = f"/admin/reports/{report_model.id}"
            return {"id": report_model.id}
        except:
            raise HTTPBadRequest("Cannot register your report model.")

    def get(self) -> dict:
        session = self.request.dbsession
        rm = (
            session.query(ReportModel)
            .filter(ReportModel.id == self.report_models_id)
            .one_or_none()
        )
        if rm:
            return ReportModelSchema().dump(rm)
        else:
            raise HTTPNotFound()

    def patch(self) -> None:
        pass

    def delete(self) -> None:
        session = self.request.dbsession
        session.query(ReportModel).filter(
            ReportModel.id == self.report_models_id
        ).delete()
        self.request.response.status_code = 204
