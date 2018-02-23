from setuptools import setup, find_packages

setup(
    name='dmc-cli',
    version='0.4',
    packages=['src'],
    include_package_data=True,
    install_requires=[
        'Click',
        'Flask',
        'Flask-RESTful',
        'Flask-Twisted',
        'requests',
        'Twisted',
    ],
    entry_points='''
        [console_scripts]
        dmc-server=src.cli:dmc_server
        dmc-agent=src.cli:dmc_agent
        dmc-devices=src.cli:dmc_devices
    ''',
)
