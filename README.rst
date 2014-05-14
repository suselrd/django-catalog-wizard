==========================
Django Catalog Wizard
==========================

Catalog Wizard for Django>=1.6.1

Allows to configure (by defining the project setting CATALOGS) all the required catalogs.
A Catalog is defined as an interchangeable set of different templates for a list of "catalogue items", to which you may
apply one or more filters (from the configured filter tray) and group according to specified criteria.

Any Django model can be a "catalogue item", only by adding a decorator to model definition.

There are a variety of provided Filters and Groupers, but the component could work with any derived class, so it is extensible.

The component integrates nicely with django-social-graph

Changelog
=========

0.1.0
-----

PENDING...

Notes
-----

PENDING...

Usage
-----

1. Run ``python setup.py install`` to install.

2. Modify your Django settings to use ``catalog``:

3. Configure CATALOGS setting. An example is distributed in catalog/tests module.

