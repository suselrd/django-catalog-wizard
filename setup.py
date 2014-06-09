from setuptools import setup, find_packages

setup(
    name = "django-catalog-wizard",
    #url = "http://github.com/suselrd/django-catalog-wizard/",
    author = "Susel Ruiz Duran",
    author_email = "suselrd@gmail.com",
    version = "0.1.5",
    packages = find_packages(),
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
    include_package_data=True,
)
