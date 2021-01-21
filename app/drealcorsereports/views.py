""" Cornice services.
"""
from cornice import Service


hello = Service(name="hello", path="/api", description="Simplest app")


@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    del request
    return {"Hello": "World"}


class MockApi:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="get_report_models", renderer="json")
    def getAll(self):
        return [
            {
                "id": "1",
                "title": "TestTitle",
                "layer": "TestLayer"
            },
            {
                "id": "2",
                "title": "TestTitle2",
                "layer": "TestLayer2"
            }
        ]

    @view_config(route_name="get_report_model_by_id1", renderer="json")
    def getOne(self):
        return {
                "id": "1",
                "title": "TestTitle",
                "layer": "TestLayer",
                "properties":
                    [
                        {"type": "string", "name": "Name", "required": True},
                        {"type": "string", "name": "Description", "required": False},
                        {"type": "number", "name": "Nr", "required": False}
                    ]
            }

    @view_config(route_name="get_report_model_by_id2", renderer="json")
    def getTwo(self):
        return {
                "id": "2",
                "title": "TestTitle2",
                "layer": "TestLayer2",
                "properties":
                    [
                        {"type": "string", "name": "Title", "required": True},
                        {"type": "number", "name": "Length", "required": True},
                        {"type": "string", "name": "Summary", "required": True}
                    ]
            }
