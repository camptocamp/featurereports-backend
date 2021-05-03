from cornice.resource import resource, view
from marshmallow_jsonschema import JSONSchema
from marshmallow_jsonschema.extensions import ReactJsonSchemaFormJSONSchema
from pyramid.request import Request
from pyramid.security import Allow, Everyone

from drealcorsereports.models.reports import ReportModel
from drealcorsereports.schemas.reports import ReportSchema
from drealcorsereports.security import is_user_reader_on_layer


@resource(
    collection_path="/jsonschemas",
    path="/jsonschemas/{id}",
    cors_origins=("*",),
)
class JsonSchemaView:
    def __init__(self, request: Request, context=None) -> None:
        self.request = request
        self.context = context

    def __acl__(self):
        acl = [
            (Allow, Everyone, "list"),
        ]
        return acl

    @view(permission="list")
    def collection_get(self) -> list:
        schemas = []

        report_models = self.request.dbsession.query(ReportModel)
        for report_model in report_models:

            if not is_user_reader_on_layer(self.request, report_model.layer_id):
                continue

            schema = ReportSchema.from_report_model(report_model)(
                exclude=[
                    "created_at",
                    "created_by",
                    "updated_by",
                    "updated_at",
                ]
            )

            schemas.append(
                {
                    "id": str(report_model.id),
                    "name": report_model.name,
                    "layer_id": report_model.layer_id,
                    "JSONSchema": JSONSchema().dump(schema),
                    "UISchema": ReactJsonSchemaFormJSONSchema().dump_uischema(schema),
                }
            )

        return schemas
