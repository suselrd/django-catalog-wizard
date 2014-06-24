from setuptools import setup

setup(
    name = "django-catalog-wizard",
    #url = "http://github.com/suselrd/django-catalog-wizard/",
    author = "Susel Ruiz Duran",
    author_email = "suselrd@gmail.com",
    version = "0.1.10",
    packages = ["catalog", "catalog.templatetags", "catalog.templates"],
    include_package_data=True,
    description = "Catalog Wizard for Django",
    install_requires=['django>=1.6.1', ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Environment :: Web Environment",
        "Framework :: Django",
    ],

)
