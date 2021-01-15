DREAL Corse Reports
===================

Create GIS features linked reports.

Create a development instance
-----------------------------

.. code-block:: bash

    git clone git@github.com:camptocamp/drealcorse-reports.git
    cd drealcorse-reports
    make meacoffee

Public interface should be available at:
http://localhost:8080/

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

    docker-compose run --rm --user `id -u ` app-tools \
        alembic -c /app/alembic.ini upgrade head

Frontend
-----------------------------

Once the composition has started a production build is available at http://localhost:8080/admin/

A development instance can be started at http://localhost:3000 by adding `front-server` service from `docker-compose.override.sample.yaml <docker-compose.override.sample.yaml>`_.

There are make targets for formatting and tests. Other npm tasks (like installing new dependencies) can be executed within the container that is mapped to the host:

.. code-block:: bash

    docker exec -it drealcorse-reports_front-server_1 /bin/bash

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
