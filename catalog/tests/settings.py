# coding=utf-8

DEBUG = True

SITE_ID = 1

SECRET_KEY = 'blabla'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '127.0.0.1:6379',
    },
}


CATALOGS = {
    'properties': {
        'FILTER_TRAY': {
            'operation_type': {
                'type': 'catalog.filters.ForeignKeyValueFilter',
                'args': ['operation_type'],
            },
            'budget_min': {
                'type': 'catalog.filters.AttributeMinLimitFilter',
                'args': ['price']
            },
            'budget_max': {
                'type': 'catalog.filters.AttributeMaxLimitFilter',
                'args': ['price']
            },
            'name': {
                'type': 'catalog.filters.AttributeValueFilter',
                'args': ['property__name']
            },
            'name_contains': {
                'type': 'catalog.filters.AttributeContainsFilter',
                'args': ['property__name'],
                'kwargs': {
                    'case_insensitive': True
                }
            },
            'keyword': {
                'type': 'catalog.filters.AttributeSetContainsFilter',
                'args': ['property__name', 'details'],
                'kwargs': {
                    'case_insensitive': True
                }
            },
            'liked_by': {
                'type': 'catalog.graph_filters.RelationExistenceFilter',
                'args': ['Liked By', 'django.contrib.auth.models.User']
            }
        },
        'DEFAULT_VIEW_TYPE': 'grid',
        'VIEW_TYPES': {
            'grid': 'catalog/grid.html',
            'slide': 'catalog/slide.html'
        },
        'DEFAULT_GROUP_BY': 'ungrouped',
        'GROUP_BY_OPTIONS': {
            'ungrouped': None,
            'status': {
                'type': 'catalog.groupings.AttributeValueGrouping',
                'args': ['status'],
                'kwargs': {
                    'aggregate': {
                        'total': {
                            'type': 'Sum',
                            'attribute': 'price'
                        },
                        'average': {
                            'type': 'Avg',
                            'attribute': 'price'
                        }
                    }
                }

            },
            'owner': {
                'type': 'catalog.groupings.AttributeValueGrouping',
                'args': ['property__owner'],
                'kwargs': {
                    'aggregate': {
                        'total': {
                            'type': 'Sum',
                            'attribute': 'price'
                        },
                        'average': {
                            'type': 'Avg',
                            'attribute': 'price'
                        }
                    }
                }
            },
            'ownername': {
                'type': 'catalog.groupings.AttributeValueGrouping',
                'args': ['property__owner__username'],
                'kwargs': {
                    'aggregate': {
                        'total': {
                            'type': 'Sum',
                            'attribute': 'price'
                        },
                        'average': {
                            'type': 'Avg',
                            'attribute': 'price'
                        }
                    }
                }
            }
        }
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'catalog',
    'catalog.tests',
    # comment the following line if you don't want to work with django-social-graph
    'social_graph'
]

ROOT_URLCONF = 'catalog.tests.urls'