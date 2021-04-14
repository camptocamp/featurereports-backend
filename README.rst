DREAL Corse Reports
===================

Create GIS features linked reports.

Create a development instance
-----------------------------

.. code-block:: bash

    git clone git@github.com:camptocamp/drealcorse-reports.git
    cd drealcorse-reports
    make meacoffee

Admin interface should be available at:
http://localhost:8080/admin/

Note that you may need to add some headers (for example using Chrome extension ModHeader)
to be able to play with data in the admin interface:

* sec-username: testadmin
* sec-roles: ROLE_REPORTS_ADMIN

To access the interface behind the georchestra proxy

* create a new line in your `/etc/hosts` :

.. code-block:: bash

    127.0.1.1 georchestra.mydomain.org

* launch the compo : `make meacoffee`
* access the interface at https://georchestra.mydomain.org/mapstore-reports/admin/?login
* login with:
   - identifiant: testadmin
   - password: testadmin
* if you have a certificate issue :

.. code-block:: bash

    make cert

* edit access rules : https://georchestra.mydomain.org/geoserver -> Security -> Data (left panel, near bottom)
To display reports you need "read" access on corresponding layer.
To create or edit reports you need "write" access on corresponding layer.
To create or edit report models you need "admin" access on corresponding layer.  

Generate a new alembic revision
-------------------------------

Before the first release we will overwrite the first migration:

.. code-block:: bash

   make regenerate-first-migration

Generate a new alembic migration:

.. code-block:: bash

    docker-compose run --rm --user `id -u` \
      -v "${PWD}/app/drealcorsereports:/app/drealcorsereports" \
      app \
      alembic -c /app/alembic.ini revision --autogenerate -m 'Description'

Now you can try it:

.. code-block:: bash

    make initdb

Frontend
--------

Once the composition has started a production build is available at http://localhost:8080/admin/

A development instance can be started at http://localhost:3000 by adding `front-server` service from `docker-compose.override.sample.yaml <docker-compose.override.sample.yaml>`_.

There are make targets for formatting and tests. Other npm tasks (like installing new dependencies) can be executed within the container that is mapped to the host:

.. code-block:: bash

    docker-compose exec front-server bash

Run formatting:

.. code-block:: bash

    make front-format

Run tests:

.. code-block:: bash

    make front-test

Sources can be found in `app/drealcorsereports/static/admin <app/drealcorsereports/static/admin>`_

This project was bootstrapped with `Create React App <https://github.com/facebook/create-react-app>`_

The React CLI allows to indicate the apps origin and a dev proxy to the API via the `package.json <app/drealcorsereports/static/admin/package.json>`_

.. code-block:: json

  "homepage": ".",
  "proxy": "http://app:8080",

The following headers can be handy to access restricted parts of the API in dev via a browser plugin:

.. code-block:: json

  "sec-username": "testadmin"
  "sec-roles": "ROLE_REPORTS_ADMIN"

MapStore Extension
-----------------------------

Developement:

The MapStore extension is developed on the fork: https://github.com/camptocamp/MapStoreExtension/tree/report-extension

There is a debug mode available with: `http://localhost:8081/?debug=true`.

Redux dev tools are useful for dev as MapStore follows redux.

Note the current issues:

* `npm install` needs to be run twice => https://github.com/geosolutions-it/MapStoreExtension/issues/4
* we have encountered problems with the version of the `webpack-cli` dependency => https://github.com/geosolutions-it/MapStoreExtension/issues/7
* mobile mode breaks a MapStore application with extension => https://github.com/geosolutions-it/MapStoreExtension/issues/6

Deployment:

MapStoreExtension developement has not yet been integrated into the project, since the best practices for this are still unclear.
To deploy the extension developed in the MapStoreExtension repo into the project the following steps are necessary:  

* run `npm run ext:build` in MapStoreExtension repo
* copy `MapStoreExtension/dist/ReportExtension.zip` into `georchestra_datadir/mapstore/dist/extensions/`
* extract `ReportExtension.zip` and remove zip (replace ReportExtension if exists) 

Note: MapStore finds the extension bundle via the config in `georchestra_datadir/mapstore/extensions.json` 
and loads it by default if indicated in `georchestra_datadir/mapstore/localConfig.json`.