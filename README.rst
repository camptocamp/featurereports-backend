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

    rm -rf app/drealcorsereports/alembic/versions/*.py
    make psql
    DROP SCHEMA reports CASCADE;
    CREATE SCHEMA reports;
    \q

.. code-block:: bash

    docker-compose run --rm --user `id -u` app-tools \
        alembic -c /app/alembic.ini revision --autogenerate -m 'First revision'

Now you can try it:

.. code-block:: bash

    make initdb

Frontend
-----------------------------

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
