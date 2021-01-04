import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.rst")) as f:
    README = f.read()
with open(os.path.join(here, "requirements.txt")) as f:
    REQUIRES = f.read()

setup(
    name="drealcorsereports",
    version=0.1,
    description="DREAL Corse Reports",
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    keywords="web services",
    author="",
    author_email="",
    url="",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIRES,
    entry_points="""\
        [paste.app_factory]
            main=drealcorsereports:main
        [plaster.loader_factory]
            c2c = drealcorsereports.loader:Loader
            c2c+ini = drealcorsereports.loader:Loader
            c2c+egg = drealcorsereports.loader:Loader
        [plaster.wsgi_loader_factory]
            c2c = drealcorsereports.loader:Loader
            c2c+ini = drealcorsereports.loader:Loader
            c2c+egg = drealcorsereports.loader:Loader
      """,
    paster_plugins=["pyramid"],
)
