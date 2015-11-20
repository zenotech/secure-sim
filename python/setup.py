from setuptools import setup, find_packages

setup(
    name='hpc_security_poc',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click', 'pyelliptic', 'pycrypto'
    ],
    entry_points='''
        [console_scripts]
        secure_sim=poc.commands:cli
    ''',
)
