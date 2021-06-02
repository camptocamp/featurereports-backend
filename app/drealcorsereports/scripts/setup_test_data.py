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
    Report,
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
            id="ba722b44-57e1-4e78-9af6-ea00c25908b1",
            title="Rennes modele 1 aires de jeux",
            name="rennes_ajeu1",
            layer_id="espub_mob:gev_ajeu",
            created_by="ajeu",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="ajeu",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
            custom_fields=[
                ReportModelCustomField(
                    title="commentaire",
                    name="commentaire",
                    type=FieldTypeEnum.string,
                    required=True,
                ),
                ReportModelCustomField(
                    title="Booléen",
                    name="booleen",
                    type=FieldTypeEnum.boolean,
                ),
                ReportModelCustomField(
                    title="Date",
                    name="date",
                    type=FieldTypeEnum.date,
                ),
                ReportModelCustomField(
                    title="Liste déroulante",
                    name="liste_deroulante",
                    type=FieldTypeEnum.enum,
                    enum=["choix1", "choix2", "choix3"],
                ),
                ReportModelCustomField(
                    title="Photo",
                    name="photo",
                    type=FieldTypeEnum.file,
                ),
                ReportModelCustomField(
                    title="Valeur numérique",
                    name="valeur_numerique",
                    type=FieldTypeEnum.number,
                ),
            ],
        ),
        ReportModel(
            id="ba722b44-57e1-4e78-9af6-ea00c25908b2",
            title="Rennes modele 2 aires de jeux",
            name="rennes_ajeu2",
            layer_id="espub_mob:gev_ajeu",
            created_by="ajeu",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="ajeu",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
            custom_fields=[
                ReportModelCustomField(
                    title="commentaire",
                    name="commentaire",
                    type=FieldTypeEnum.string,
                    required=True,
                ),
                ReportModelCustomField(
                    title="Booléen",
                    name="booleen",
                    type=FieldTypeEnum.boolean,
                ),
                ReportModelCustomField(
                    title="Date",
                    name="date",
                    type=FieldTypeEnum.date,
                ),
                ReportModelCustomField(
                    title="Liste déroulante",
                    name="liste_deroulante",
                    type=FieldTypeEnum.enum,
                    enum=["choix1", "choix2", "choix3"],
                ),
                ReportModelCustomField(
                    title="Photo",
                    name="photo",
                    type=FieldTypeEnum.file,
                ),
                ReportModelCustomField(
                    title="Valeur numérique",
                    name="valeur_numerique",
                    type=FieldTypeEnum.number,
                ),
            ],
        ),
        ReportModel(
            id="ba722b44-57e1-4e78-9af6-ea00c25908b3",
            title="Rennes modele 3 aires de jeux",
            name="rennes_ajeu3",
            layer_id="espub_mob:gev_ajeu",
            created_by="ajeu",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="ajeu",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
            custom_fields=[
                ReportModelCustomField(
                    title="commentaire",
                    name="commentaire",
                    type=FieldTypeEnum.string,
                    required=True,
                ),
                ReportModelCustomField(
                    title="Booléen",
                    name="booleen",
                    type=FieldTypeEnum.boolean,
                ),
                ReportModelCustomField(
                    title="Date",
                    name="date",
                    type=FieldTypeEnum.date,
                ),
                ReportModelCustomField(
                    title="Liste déroulante",
                    name="liste_deroulante",
                    type=FieldTypeEnum.enum,
                    enum=["choix1", "choix2", "choix3"],
                ),
                ReportModelCustomField(
                    title="Photo",
                    name="photo",
                    type=FieldTypeEnum.file,
                ),
                ReportModelCustomField(
                    title="Valeur numérique",
                    name="valeur_numerique",
                    type=FieldTypeEnum.number,
                ),
            ],
        ),
        ReportModel(
            id="ba722b44-57e1-4e78-9af6-ea00c25908b0",
            title="Rennes modele 1 jeux",
            name="rennes_jeu1",
            layer_id="espub_mob:gev_jeu",
            created_by="jeux",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="jeux",
            updated_at=datetime(2021, 1, 22, 13, 34, tzinfo=timezone.utc),
            custom_fields=[
                ReportModelCustomField(
                    title="commentaire",
                    name="commentaire",
                    type=FieldTypeEnum.string,
                    required=True,
                ),
                ReportModelCustomField(
                    title="Booléen",
                    name="booleen",
                    type=FieldTypeEnum.boolean,
                ),
                ReportModelCustomField(
                    title="Date",
                    name="date",
                    type=FieldTypeEnum.date,
                ),
                ReportModelCustomField(
                    title="Liste déroulante",
                    name="liste_deroulante",
                    type=FieldTypeEnum.enum,
                    enum=["choix1", "choix2", "choix3"],
                ),
                ReportModelCustomField(
                    title="Photo",
                    name="photo",
                    type=FieldTypeEnum.file,
                ),
                ReportModelCustomField(
                    title="Valeur numérique",
                    name="valeur_numerique",
                    type=FieldTypeEnum.number,
                ),
            ],
        ),
    ]
    dbsession.add_all(report_models)
    reports = [
        Report(
            feature_id="gev_ajeu.60",
            report_model_id="ba722b44-57e1-4e78-9af6-ea00c25908b1",
            custom_field_values={
                "commentaire": "un commentaire",
                "liste_deroulante": "choix1",
                "valeur_numerique": 3,
                "booleen": "true",
                "date": "2021-05-17",
            },
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="toto",
            updated_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        ),
        Report(
            feature_id="gev_ajeu.60",
            report_model_id="ba722b44-57e1-4e78-9af6-ea00c25908b1",
            custom_field_values={
                "commentaire": "un commentaire",
                "liste_deroulante": "choix1",
                "valeur_numerique": 3,
                "booleen": "true",
                "date": "2021-05-17",
            },
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="toto",
            updated_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        ),
        Report(
            feature_id="gev_ajeu.60",
            report_model_id="ba722b44-57e1-4e78-9af6-ea00c25908b2",
            custom_field_values={
                "commentaire": "un commentaire",
                "liste_deroulante": "choix1",
                "valeur_numerique": 3,
                "booleen": "true",
                "date": "2021-05-17",
            },
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="toto",
            updated_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        ),
        Report(
            feature_id="gev_jeu.20185",
            report_model_id="ba722b44-57e1-4e78-9af6-ea00c25908b0",
            custom_field_values={
                "commentaire": "un commentaire",
                "liste_deroulante": "choix1",
                "valeur_numerique": 3,
                "booleen": "true",
                "date": "2021-05-17",
            },
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="toto",
            updated_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        ),
        Report(
            feature_id="gev_jeu.20550",
            report_model_id="ba722b44-57e1-4e78-9af6-ea00c25908b0",
            custom_field_values={
                "commentaire": "un commentaire",
                "liste_deroulante": "choix1",
                "valeur_numerique": 3,
                "booleen": "true",
                "date": "2021-05-17",
            },
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="toto",
            updated_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        ),
        Report(
            feature_id="gev_jeu.20187",
            report_model_id="ba722b44-57e1-4e78-9af6-ea00c25908b0",
            custom_field_values={
                "commentaire": "un commentaire",
                "liste_deroulante": "choix1",
                "valeur_numerique": 3,
                "booleen": "true",
                "date": "2021-05-17",
            },
            created_by="toto",
            created_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
            updated_by="toto",
            updated_at=datetime(2021, 1, 22, 13, 33, tzinfo=timezone.utc),
        ),
    ]
    dbsession.add_all(reports)
