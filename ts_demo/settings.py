from __future__ import annotations

import os
from pathlib import Path
from typing import Type

from composed_configuration import (
    ComposedConfiguration,
    ConfigMixin,
    DevelopmentBaseConfiguration,
    HerokuProductionBaseConfiguration,
    ProductionBaseConfiguration,
    TestingBaseConfiguration,
)
from configurations import values


class GeoDjangoMixin(ConfigMixin):
    @staticmethod
    def before_binding(configuration: Type[ComposedConfiguration]):
        configuration.INSTALLED_APPS += ['django.contrib.gis']
        try:
            import re

            import osgeo

            libsdir = os.path.join(
                os.path.dirname(os.path.dirname(osgeo._gdal.__file__)), 'GDAL.libs'
            )
            libs = {
                re.split(r'-|\.', name)[0]: os.path.join(libsdir, name)
                for name in os.listdir(libsdir)
            }
            configuration.GDAL_LIBRARY_PATH = libs['libgdal']
            configuration.GEOS_LIBRARY_PATH = libs['libgeos_c']
        except Exception:
            # TODO: Log that we aren't using the expected GDAL wheel?
            pass


class SwaggerMixin(ConfigMixin):
    REFETCH_SCHEMA_WITH_AUTH = True
    REFETCH_SCHEMA_ON_LOGOUT = True
    OPERATIONS_SORTER = 'alpha'
    DEEP_LINKING = True


class TsDemoMixin(GeoDjangoMixin, SwaggerMixin, ConfigMixin):
    WSGI_APPLICATION = 'ts_demo.wsgi.application'
    ROOT_URLCONF = 'ts_demo.urls'

    BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

    RGD_GLOBAL_READ_ACCESS = values.Value(default=False)
    RGD_FILE_FIELD_PREFIX = values.Value(default=None)

    @staticmethod
    def before_binding(configuration: ComposedConfiguration) -> None:
        # Install local apps first, to ensure any overridden resources are found first
        configuration.INSTALLED_APPS = [
            'ts_demo.core.apps.CoreConfig',
        ] + configuration.INSTALLED_APPS

        # Install additional apps
        configuration.INSTALLED_APPS += [
            's3_file_field',
            'rgd',
            'rgd_imagery',
        ]

        configuration.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'].append(
            'rest_framework.authentication.BasicAuthentication'
        )

    # This cannot have a default value, since the password and database name are always
    # set by the service admin
    DATABASES = values.DatabaseURLValue(
        environ_name='DATABASE_URL',
        environ_prefix='DJANGO',
        environ_required=True,
        # Additional kwargs to DatabaseURLValue are passed to dj-database-url
        engine='django.contrib.gis.db.backends.postgis',
        conn_max_age=600,
    )


class DevelopmentConfiguration(TsDemoMixin, DevelopmentBaseConfiguration):
    pass


class TestingConfiguration(TsDemoMixin, TestingBaseConfiguration):
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True


class ProductionConfiguration(TsDemoMixin, ProductionBaseConfiguration):
    pass


class HerokuProductionConfiguration(TsDemoMixin, HerokuProductionBaseConfiguration):
    DATABASES = values.DatabaseURLValue(
        environ_name='DATABASE_URL',
        environ_prefix=None,
        environ_required=True,
        engine='django.contrib.gis.db.backends.postgis',
        conn_max_age=600,
        ssl_require=True,
    )
