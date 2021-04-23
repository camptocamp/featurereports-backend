"""Main entry point
"""
from pyramid.config import Configurator


def main(global_config, **settings):
    del global_config
    settings['tm.commit_veto'] = 'pyramid_tm.default_commit_veto'

    config = Configurator(settings=settings)

    config.include("drealcorsereports.models.includeme")
    config.include("drealcorsereports.security")
    config.include("cornice")
    config.add_static_view("admin", "/opt/drealcorsereports/static/admin/build")

    config.scan("drealcorsereports.views")

    return config.make_wsgi_app()
