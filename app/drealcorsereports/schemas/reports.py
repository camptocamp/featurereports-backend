import marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from drealcorsereports.models.reports import Report, ReportModel


class ReportSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Report
        load_instance = True
        include_relationships = True

    created_at = auto_field(dump_only=True)
    created_by = auto_field(dump_only=True)
    updated_by = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)


class ReportModelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ReportModel
        load_instance = True
        include_relationships = False

    created_by = auto_field(dump_only=True)
    created_at = auto_field(dump_only=True)
    updated_by = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)

    @marshmallow.validates("name")
    def validate_name_unique(self, value):
        request = self.context["request"]
        query = (
            request.dbsession.query(ReportModel)
            .filter(ReportModel.name == value)
            .filter(ReportModel.id != request.matchdict.get("id", None))
        )
        if query.count() > 0:
            raise marshmallow.ValidationError(
                f"Report model named {value} already exists."
            )
