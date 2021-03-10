from typing import Dict
from uuid import UUID

from cornice.resource import resource
from drealcorsereports.models.reports import ReportModel, Report
from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request


@resource(
    path="/tjs/{report_model_id}",
    cors_origins=("*",),
)
class TjsView:
    def __init__(self, request: Request, context=None) -> None:
        del context
        self.request = request
        self.model_id = UUID(request.matchdict["report_model_id"])

    def get(self):
        rm = (
            self.request.dbsession.query(ReportModel)
            .filter(id == self.model_id)
            .one_or_none()
        )
        if rm is None:
            raise HTTPNotFound()
        schema = Report.__table_args__["schema"]
        return {"view_name": f"{schema}.v_report_"}

    def post(self) -> Dict[str, str]:
        """
        create a postgresql view
        """
        dbsession = self.request.dbsession
        rm = dbsession.query(ReportModel).filter(id == self.model_id).one_or_none()
        if rm is None:
            raise HTTPNotFound()
        rows = [
            f"custom_field_values->>{k} as {k}"
            for k in rm.custom_field_schema["properties"].keys()
        ]
        rows = ", ".join(rows)
        table_name = Report.__tablename__
        schema = Report.__table_args__["schema"]
        f"""
        CREATE VIEW {schema}.v_report_{rm.name} AS SELECT {rows} FROM {schema}.{table_name};
        """
        return {"view_name": f"{schema}.v_report_{rm.name}"}

    def delete(self) -> None:
        """Delete a postgresql view"""
        rm = (
            self.request.dbsession.query(ReportModel)
            .filter(id == self.model_id)
            .one_or_none()
        )
        if rm is None:
            raise HTTPNotFound()
        self.request.dbsession.execute(f"""DROP VIEW {rm.name}""")
        self.request.response.status_code = 204
