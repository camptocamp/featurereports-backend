import marshmallow
import marshmallow_sqlalchemy
from marshmallow import fields
from marshmallow_enum import EnumField
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from drealcorsereports.models.reports import (
    FieldTypeEnum,
    Report,
    ReportModel,
    ReportModelCustomField,
)
from drealcorsereports.security import (
    is_user_admin_on_layer,
    is_user_writer_on_layer,
)


class ReportSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Report
        load_instance = True
        include_relationships = False

    report_model_id = fields.UUID()
    created_at = auto_field(dump_only=True)
    created_by = auto_field(dump_only=True)
    updated_by = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)

    @marshmallow.validates("report_model_id")
    def validate_layer_writer(self, value):
        request = self.context["request"]
        report_model = request.dbsession.query(ReportModel).get(value)
        if not is_user_writer_on_layer(request, report_model.layer_id):
            raise marshmallow.ValidationError(
                f"You're not writer on layer {report_model.layer_id}."
            )

    @marshmallow.validates_schema
    def validate_custom_field_values(self, data, **kwargs):
        del kwargs
        request = self.context["request"]
        report_model_id = data["report_model_id"]
        custom_field_values = data["custom_field_values"]
        report_model = request.dbsession.query(ReportModel).get(report_model_id)
        custom_fields = {f.name: f for f in report_model.custom_fields}
        for name in custom_field_values:
            if name not in custom_fields:
                raise marshmallow.ValidationError(
                    f"Unexpected field {name}", field_name="custom_field_values"
                )


class ReportModelFieldSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ReportModelCustomField
        load_instance = True
        include_relationships = False

    type = EnumField(FieldTypeEnum)


class ReportModelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ReportModel
        load_instance = True
        include_relationships = False

    created_by = auto_field(dump_only=True)
    created_at = auto_field(dump_only=True)
    updated_by = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True)

    custom_fields = marshmallow.fields.List(
        marshmallow_sqlalchemy.fields.Nested(ReportModelFieldSchema)
    )

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
