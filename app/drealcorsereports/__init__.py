"""Main entry point
"""
from pyramid.config import Configurator


def main(global_config, **settings):
    del global_config
    config = Configurator(settings=settings)
    config.include("cornice")
    config.scan("drealcorsereports.views")
    config.add_static_view("static", "adminfront")
    return config.make_wsgi_app()
