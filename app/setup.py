import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.rst")) as f:
    README = f.read()
with open(os.path.join(here, "requirements.txt")) as f:
    REQUIRES = f.read()

setup(
    name="featurereports",
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
        [console_scripts]
            setup_test_data = featurereports.scripts.setup_test_data:main
        [paste.app_factory]
            main=featurereports:main
        [plaster.loader_factory]
            c2c = featurereports.loader:Loader
            c2c+ini = featurereports.loader:Loader
            c2c+egg = featurereports.loader:Loader
        [plaster.wsgi_loader_factory]
            c2c = featurereports.loader:Loader
            c2c+ini = featurereports.loader:Loader
            c2c+egg = featurereports.loader:Loader
      """,
    paster_plugins=["pyramid"],
)
