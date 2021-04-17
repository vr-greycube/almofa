# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in almofa/__init__.py
from almofa import __version__ as version

setup(
	name='almofa',
	version=version,
	description='Sales customizations app.',
	author='Greycube',
	author_email='info@greycube.in',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
