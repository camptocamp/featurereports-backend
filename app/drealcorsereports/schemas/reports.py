from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from drealcorsereports.models.reports import Report, ReportModel


class ReportSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Report
        load_instance = True
        include_relationships = True


class ReportModelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ReportModel
        load_instance = True
        include_relationships = True
