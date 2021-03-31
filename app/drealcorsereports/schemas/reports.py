import enum

import marshmallow
import marshmallow_sqlalchemy
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


CUSTOM_FIELD_TYPE_MAPPING = {
    FieldTypeEnum.boolean: marshmallow.fields.Boolean,
    FieldTypeEnum.date: marshmallow.fields.Date,
    FieldTypeEnum.file: marshmallow.fields.String,
    FieldTypeEnum.number: marshmallow.fields.Number,
    FieldTypeEnum.string: marshmallow.fields.String,
    FieldTypeEnum.enum: EnumField,
}


def create_custom_field_field(
    custom_field: ReportModelCustomField,
) -> marshmallow.fields.Field:
    """
    Create and return a marshmallow Field for the passed ReportModelCustomField.
    """
    field_class = CUSTOM_FIELD_TYPE_MAPPING[custom_field.type]

    kwargs = {}
    if custom_field.type == FieldTypeEnum.enum:
        kwargs["enum"] = enum.Enum(
            custom_field.name.capitalize(),
            custom_field.enum,
        )

    field = field_class(required=custom_field.required, **kwargs)
    return field


def create_custom_fields_schema(report_model: ReportModel) -> marshmallow.Schema:
    """
    Create and return a mashmallow Schema for the custom fields of the passed ReportModel.
    """
    return marshmallow.Schema.from_dict(
        {
            custom_field.name: create_custom_field_field(custom_field)
            for custom_field in report_model.custom_fields
        },
        name="CustomFieldsSchema",
    )


class ReportSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Report
        load_instance = True
        include_relationships = False
        react_uischema_extra = {
            "ui:order": [
                "id",
                "feature_id",
                "report_model_id",
                "custom_field_values",
            ],
        }

    id = auto_field(metadata={"ui:widget": "hidden"})
    feature_id = auto_field(metadata={"ui:widget": "hidden"})
    report_model_id = auto_field(metadata={"ui:widget": "hidden"})
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

    @classmethod
    def from_report_model(cls, report_model):
        """
        Create an return an extended ReportSchema with a nested Schema for the custom fields' values.
        Used to generate the JSONSchema.
        """
        return cls.from_dict(
            {
                "report_model_id": auto_field(
                    default=str(report_model.id), metadata={"ui:widget": "hidden"}
                ),
                "custom_field_values": marshmallow.fields.Nested(
                    create_custom_fields_schema(report_model),
                    metadata={
                        "ui:order": [
                            custom_field.name
                            for custom_field in report_model.custom_fields
                        ],
                    },
                ),
            },
            name="ExtendedReportSchema",
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
