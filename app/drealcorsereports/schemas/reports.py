import marshmallow
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from drealcorsereports.models.reports import Report, ReportModel
from drealcorsereports.security import is_user_admin_on_layer


class ReportSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Report
        load_instance = True
        #include_relationships = True
    
    report_model_id = fields.String()
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

    @marshmallow.validates("layer_id")
    def validate_layer_admin(self, value):
        request = self.context["request"]
        if not is_user_admin_on_layer(request, value):
            raise marshmallow.ValidationError(f"You're not admin on layer {value}.")
