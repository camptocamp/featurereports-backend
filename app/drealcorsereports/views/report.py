from datetime import datetime, timezone
from uuid import UUID

from cornice.resource import resource, view
from cornice.validators import marshmallow_body_validator
from drealcorsereports.security import (
    is_user_admin_on_layer,
    is_user_reader_on_layer,
    is_user_writer_on_layer,
)
from pyramid.request import Request
from pyramid.exceptions import HTTPNotFound

from drealcorsereports.models.reports import Report, ReportModel
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
        """
        ROLE_REPORTS_ADMIN have the right to do anything
        For a specific user, we check in geoserver what right it has (admin, reader, writer)
        In case of POST, the id of the report is not specified, we need to sneak
        into the playload to look for the report_model_id to knows the layer
        associated to this report and find which permission to look for in geosever
        """
        acl = [
            (Allow, "ROLE_REPORTS_ADMIN", ("list", "add", "view", "delete")),
        ]
        session = self.request.dbsession
        try:
            layer_id = ""
            if "report_id" in self.__dict__:
                layer_id = (
                    session.query(ReportModel.layer_id)
                    .join(Report)
                    .filter(Report.id == self.report_id)
                    .one()
                )[0]
            else:
                # search for data in payload. Even if the payload hasn't been validated by marshamllow 😱
                report_model_id = self.request.json["report_model_id"]
                layer_id = (
                    session.query(ReportModel.layer_id)
                    .filter(ReportModel.id == report_model_id)
                    .one()
                )[0]

            # This code path could be optimized (3 calls to geoserver) to 1 call
            if is_user_reader_on_layer(self.request, layer_id):
                acl.append(
                    (
                        Allow,
                        self.request.authenticated_userid,
                        ("list", "add", "view", "delete"),
                    )
                )
            if is_user_writer_on_layer(self.request, layer_id):
                acl.append(
                    (
                        Allow,
                        self.request.authenticated_userid,
                        ("list", "add", "view", "delete"),
                    )
                )
            if is_user_admin_on_layer(self.request, layer_id):
                acl.append(
                    (
                        Allow,
                        self.request.authenticated_userid,
                        (
                            "list",
                            "add",
                            "view",
                        ),
                    )
                )
        except Exception as e:
            """
            in case of failure, just don't add any permission and let the permission code deals with missing credentials
            """
            pass

        return acl

    # FIXME listing all reports is useless. Listing reports by report model makes more senses.
    # @view(permission="list")
    # def collection_get(self) -> list:
    #     session = self.request.dbsession
    #     reports = session.query(Report)
    #     report_schema = ReportSchema()
    #     return [report_schema.dumps(r) for r in reports]

    @view(permission="list")
    def get_report_by_layer_id(self) -> list:
        layer_id = UUID(self.request.matchdict("layer_id"))
        reports = (
            self.request.dbsession.query(Report)
            .join(ReportModel)
            .filter(ReportModel.layer_id == layer_id)
            .all()
        )
        return ReportSchema.dump(reports, many=True)

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
