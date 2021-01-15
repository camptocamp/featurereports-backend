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

    @view_config(route_name="get_report_model_by_id", renderer="json")
    def getOne(self):
        return {
                "id": "1",
                "title": "TestTitle",
                "layer": "TestLayer"
            }
