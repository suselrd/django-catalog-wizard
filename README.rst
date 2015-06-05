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

1.0.0
-----
- New decorator for catalog enabled models, allowing to pass a dictionary mapping contexts to templates for that specific model.
- New filters for date attributes.
- New groupings for date attributes.
- Catalog views now returns the total result count (even if the results are paginated).
- Performance improvements.

0.4.0
-----
Spanish Translations.

0.3.2
-----
Fix in request aware filters.

0.3.1
-----
Added BoolAttributeValueFilter.
Added RequestAwareFilterMixin, for filters that need request information to perform the filtering process.

0.3.0
-----
Added Django 1.7 support.


0.2.1
-----
Fix for not requiring django-social-graph installation.

0.2.0
-----
Added South support.
Added search logging support.

0.1.11
-----
Added the possibility of setting fixed filters, that is, filters that always applies to catalog's queryset,
without user decision.

0.1.10
-----
Added kwargs to all filters init method.

0.1.9
-----
Fix in CatalogView's max_page determination for grouped lists.

0.1.8
-----
Fix in CatalogView's 'get_form_kwargs' method

0.1.7
-----
Fix pagination and ordering operations execution order.
Fix in ChildRelationAttributeRangeFilter

0.1.6
-----
ModelContextTemplate model registered for django admin.

0.1.5
-----
Graph filters now expects a comma separated target_pk argument, so we can filter objects according the existence
(or attribute, or time of) their edges with multiple targets simultaneously.

0.1.4
-----
Added support for using a FILTER & ORDER form with CatalogView
Added support for compound filters

0.1.3
-----
Added support for sorting the result list, grouped or not.
Pagination now takes place after grouping, so every group object list gets paginated individually.

0.1.2
-----
Added custom template tag for getting the proper template to use for rendering a given object in a given context.

0.1.1
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

