""" Cornice services.
"""
from cornice import Service
from pyramid.view import view_config


hello = Service(name="hello", path="/", description="Simplest app")


@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    del request
    return {"Hello": "World"}


class MockApi:
    def __init__(self, request):
        self.request = request

    @view_config(route_name="mock_api", renderer="json")
    def hello(self):
        return {"Hello": "API"}
