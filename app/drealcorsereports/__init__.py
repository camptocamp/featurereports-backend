"""Main entry point
"""
from pyramid.config import Configurator

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID
from pyramid.renderers import JSON


def datetime_adapter(obj, request):
    if obj is not None:
        return obj.isoformat()


def to_string_adapter(obj, request):
    if obj is not None:
        return str(obj)


def to_float_adapter(obj, request):
    if obj is not None:
        return float(obj)


def main(global_config, **settings):
    del global_config
    config = Configurator(settings=settings)

    json_renderer = JSON()
    json_renderer.add_adapter(datetime, datetime_adapter)
    json_renderer.add_adapter(UUID, to_string_adapter)
    json_renderer.add_adapter(timedelta, to_string_adapter)
    json_renderer.add_adapter(Decimal, to_float_adapter)
    config.add_renderer("json", json_renderer)
    config.include("drealcorsereports.models.includeme")

    config.include("cornice")
    config.add_static_view("admin", "/opt/drealcorsereports/static/admin/build")

    config.scan("drealcorsereports.views")
    return config.make_wsgi_app()
