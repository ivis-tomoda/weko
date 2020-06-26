# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 National Institute of Informatics.
#
# INVENIO-ResourceSyncServer is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module of invenio-resourcesyncserver."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'coverage>=4.5.3,<5.0.0',
    'mock>=3.0.0,<4.0.0',
    'pytest>=4.6.4,<5.0.0',
    'pytest-cache',
    'pytest-cov',
    'pytest-pep8',
    'pytest-invenio',
    'responses',
]

extras_require = {
    'docs': [
        'Sphinx>=1.5.1',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=3.0.0,<5',
]

install_requires = [
    'Flask-BabelEx>=0.9.3',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_resourcesyncserver', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-resourcesyncserver',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio TODO',
    license='MIT',
    author='National Institute of Informatics',
    author_email='wekosoftware@nii.ac.jp',
    url='https://github.com/RCOSDP/invenio-resourcesyncserver',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_resourcesyncserver = '
            'invenio_resourcesyncserver:InvenioResourceSyncServer',
        ],
        'invenio_base.blueprints': [
            'invenio_resourcesyncserver = '
            'invenio_resourcesyncserver.views:blueprint',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_resourcesyncserver',
        ],
        'invenio_admin.views': [
            'invenio_admin_resource_list = '
            'invenio_resourcesyncserver.admin:invenio_admin_resource_list',
            'invenio_admin_change_list = '
            'invenio_resourcesyncserver.admin:invenio_admin_change_list',
        ],
        'invenio_assets.bundles': [
            'invenio_admin_resource_js = '
            'invenio_resourcesyncserver.bundles:invenio_admin_resource_js',
            'invenio_admin_resource_css = '
            'invenio_resourcesyncserver.bundles:invenio_admin_resource_css',
            'invenio_admin_change_list_js = '
            'invenio_resourcesyncserver.bundles:invenio_admin_change_list_js',
            'invenio_admin_change_list_css = '
            'invenio_resourcesyncserver.bundles:invenio_admin_change_list_css',
        ],
        'invenio_db.models': [
            'invenio_resourcesyncserver = invenio_resourcesyncserver.models',
        ],
        # TODO: Edit these entry points to fit your needs.
        # 'invenio_access.actions': [],
        # 'invenio_admin.actions': [],
        # 'invenio_assets.bundles': [],
        # 'invenio_base.api_apps': [],
        # 'invenio_base.api_blueprints': [],
        # 'invenio_base.blueprints': [],
        # 'invenio_celery.tasks': [],
        # 'invenio_db.models': [],
        # 'invenio_pidstore.minters': [],
        # 'invenio_records.jsonresolver': [],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 1 - Planning',
    ],
)
