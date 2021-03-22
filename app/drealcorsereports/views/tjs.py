from cornice import Service
from pyramid.request import Request

tjs = Service(path="/toto/export.csv", name="tjs", renderer="json")


@tjs.get()
def tjs_export(request: Request) -> None:
    p = dict()
    for k, v in request.headers.items():
        p[str(k)] = str(v)
    return p
