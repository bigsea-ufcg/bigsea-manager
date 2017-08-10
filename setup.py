from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='Application Manager',

    version='0.1.0',

    description='Python framework to control application progress on sahara',

    url='',

    author='Telles Nobrega',
    author_email='tellesnobrega@gmail.com',

    license='Apache 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: Apache 2.0',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',

    ],
    keywords='webservice sahara application management',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=['flask'],

    entry_points={
        'console_scripts': [
            'application_manager=application_manager.cli.main:main',
        ],
        'application_manager.execution.plugins': [
            'sahara=application_manager.plugins.sahara.plugin:SaharaProvider',
            'sahara_hdfs=application_manager.plugins.sahara_hdfs.plugin:SaharaHDFSProvider',
            'fake=application_manager.plugins.test_plugin.plugin:FakeProvider',
            'os_generic=application_manager.plugins.openstack_generic.plugin:OpenStackGenericProvider',
            'chronos=application_manager.plugins.chronos.plugin:ChronosGenericProvider'
        ],
    },
)

