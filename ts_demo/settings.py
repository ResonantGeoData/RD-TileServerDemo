from __future__ import annotations

from pathlib import Path

from composed_configuration import (
    ComposedConfiguration,
    ConfigMixin,
    DevelopmentBaseConfiguration,
    HerokuProductionBaseConfiguration,
    ProductionBaseConfiguration,
    TestingBaseConfiguration,
)


class TsDemoMixin(ConfigMixin):
    WSGI_APPLICATION = 'ts_demo.wsgi.application'
    ROOT_URLCONF = 'ts_demo.urls'

    BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

    @staticmethod
    def before_binding(configuration: ComposedConfiguration) -> None:
        # Install local apps first, to ensure any overridden resources are found first
        configuration.INSTALLED_APPS = [
            'ts_demo.core.apps.CoreConfig',
        ] + configuration.INSTALLED_APPS

        # Install additional apps
        configuration.INSTALLED_APPS += [
            's3_file_field',
        ]


class DevelopmentConfiguration(TsDemoMixin, DevelopmentBaseConfiguration):
    pass


class TestingConfiguration(TsDemoMixin, TestingBaseConfiguration):
    pass


class ProductionConfiguration(TsDemoMixin, ProductionBaseConfiguration):
    pass


class HerokuProductionConfiguration(TsDemoMixin, HerokuProductionBaseConfiguration):
    pass
