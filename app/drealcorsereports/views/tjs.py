from cornice import Service
from pyramid.request import Request

tjs = Service(path="/reports/export.csv", name="tjs", renderer="json")


@tjs.get()
def tjs_export(request: Request) -> None:
    del request
