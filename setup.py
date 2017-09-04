#!/usr/bin/env python
from setuptools import setup


DESCRIPTION = "A demo for manipulating trees in Django using PostgreSQL"
LICENSE = u'MIT'
NAME = 'django-ltree-demo'
PACKAGES = ['demo']
URL = 'https://github.com/novafloss/django-ltree-demo'
VERSION = 1.0


if __name__ == '__main__':
    setup(
        description=DESCRIPTION,
        include_package_data=True,
        license=LICENSE,
        name=NAME,
        packages=PACKAGES,
        url=URL,
        version=VERSION,
    )
