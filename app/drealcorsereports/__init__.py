"""Main entry point
"""
from pyramid.config import Configurator


def main(global_config, **settings):
    del global_config
    config = Configurator(settings=settings)

    config.include("drealcorsereports.models.includeme")
    config.include("drealcorsereports.security")
    config.include("cornice")
    config.add_route("get_report_models", "/admin/report_models")
    config.add_route("get_report_model_by_id1", "/admin/report_models/1")
    config.add_route("get_report_model_by_id2", "/admin/report_models/2")
    config.add_static_view("admin", "/opt/drealcorsereports/static/admin/build")

    config.scan("drealcorsereports.views")

    return config.make_wsgi_app()
