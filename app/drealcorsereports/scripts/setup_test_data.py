# coding=utf-8
import argparse
from datetime import datetime, timezone

import requests
from pyramid.scripts.common import get_config_loader

from drealcorsereports.models import get_engine, get_session_factory
from drealcorsereports.models.reports import (
    FieldTypeEnum,
    ReportModel,
    ReportModelCustomField,
)


def main():
    parser = argparse.ArgumentParser(description="Setup test dataset")
    parser.add_argument(
        "config_uri",
        default="c2c://drealcorsereports.ini",
        help="The URI to the configuration file",
    )
    parser.add_argument(
        "config_vars",
        nargs="*",
        default=[],
        help=(
            "Variables required by the config file."
            " For example, http_port=%(http_port)s would expect http_port=8080 to be passed here."
        ),
    )
    args = parser.parse_args()

    loader = get_config_loader(args.config_uri)
    loader.setup_logging()
    settings = loader.get_wsgi_app_settings(defaults=args.config_vars)

    # setup_geoserver_rules(settings)

    engine = get_engine(settings)
    # wait_for_db(engine)

    session_factory = get_session_factory(engine)
    dbsession = session_factory()
    with dbsession.transaction:
        setup_test_data(dbsession)


# superseeded by test_data/geoserver_to_datadir/layers.properties 
def setup_geoserver_rules(settings):
    geoserver_url = settings["geoserver_url"]

    response = requests.post(
        f"{geoserver_url}/rest/security/acl/layers",
        headers={
            "sec-roles": "ROLE_ADMINISTRATOR",
            "sec-username": "geoserver_privileged_user",
            "Content-Type": "application/json; charset=utf8",
            "Accept": "application/json",
        },
        data='{"*.*.a": "ROLE_ADMINISTRATOR"}',
    )
    response.raise_for_status()


def setup_test_data(dbsession):
    report_models = [
        ReportModel(
            title="Model1",
            name="first_model",
            layer_id="geor:public_layer",
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="tata",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
            custom_fields=[
                ReportModelCustomField(
                    title="commentaire",
                    name="commentaire",
                    type=FieldTypeEnum.string,
                )
            ],
        ),
        ReportModel(
            title="Model2",
            name="second_model",
            layer_id="geor:public_layer",
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="tata",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
            custom_fields=[
                ReportModelCustomField(
                    title="commentaire",
                    name="commentaire",
                    type=FieldTypeEnum.string,
                )
            ],
        ),
    ]
    dbsession.add_all(report_models)
