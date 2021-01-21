from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, SQLAlchemySchema, auto_field
from drealcorsereports.models.reports import Report, ReportModel


class ReportSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Report
        load_instance = True
        include_relationships = True
    id = auto_field(dump_only=True)
    created_at = auto_field(dump_only=True)
    created_by = auto_field(dump_only=True)



class ReportModelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ReportModel
        load_instance = True
        include_relationships = True

    id = auto_field(dump_only=True)
    created_at = auto_field(dump_only=True)
    created_by = auto_field(dump_only=True)
