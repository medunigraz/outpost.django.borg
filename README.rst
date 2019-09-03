===================
Outpost Django Borg
===================

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |codecov|

.. |docs| image:: https://readthedocs.org/projects/outpost/badge/?style=flat
    :target: https://readthedocs.org/projects/outpost.django.borg
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/medunigraz/outpost.django.borg.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/medunigraz/outpost.django.borg

.. |requires| image:: https://requires.io/github/medunigraz/outpost.django.borg/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/medunigraz/outpost.django.borg/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/medunigraz/outpost.django.borg/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/medunigraz/outpost.django.borg

.. end-badges

Manage backup repositories for Borg backup.

* Free software: BSD license

Documentation
=============

https://outpost.django.borg.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
