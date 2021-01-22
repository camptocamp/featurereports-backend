""" Cornice services.
"""
from cornice import Service


hello = Service(name="hello", path="/api", description="Simplest app")


@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    del request
    return {"Hello": "World"}
