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
