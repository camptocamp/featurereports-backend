import zope
from cornice import Service
from drealcorsereports.models.reports import ReportModel, ReportModelCustomField, Report
from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from sqlalchemy import text

tjs = Service(path="/tjs/reports/{id}", name="tjs", renderer="json")


@tjs.post()
def tjs_export(request: Request) -> dict:
    id = request.matchdict["id"]
    report_model = request.dbsession.query(ReportModel).get(id)
    if report_model is None:
        raise HTTPNotFound()
    fields = request.dbsession.query(ReportModelCustomField.name).filter(ReportModelCustomField.report_model_id == id)
    schema = ReportModel.__table_args__["schema"]
    report_table_name = Report.__tablename__
    view_columns = ", ".join([f"custom_field_values->>'{f.name}' as {f.name}" for f in fields])
    request.dbsession.execute(text(f"""
    CREATE OR REPLACE VIEW {schema}.v_tjs_view_{report_model.name} 
        AS SELECT {view_columns} FROM {schema}.{report_table_name}  
    """))
    # mark the session as dirty, if not transation manager will rollback the transaction.
    # ¯\_(ツ)_/¯
    zope.sqlalchemy.mark_changed(request.dbsession)
    return {"view": f"{schema}.v_tjs_view_{report_model.name}"}
