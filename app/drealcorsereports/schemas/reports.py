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
from drealcorsereports.security import is_user_admin_on_layer


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
