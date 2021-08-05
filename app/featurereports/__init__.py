"""Main entry point
"""
from pyramid.config import Configurator


def main(global_config, **settings):
    del global_config
    settings["tm.commit_veto"] = "pyramid_tm.default_commit_veto"

    config = Configurator(settings=settings)

    config.include("featurereports.models.includeme")
    config.include("featurereports.security")
    config.include("cornice")
    config.add_static_view("admin", "/opt/featurereports/static/admin/build")

    config.scan("featurereports.views")

    return config.make_wsgi_app()
