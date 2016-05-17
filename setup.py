from setuptools import setup, find_packages

setup(
    name='hotbackup',
    version='0.0.1',
    description='A utility to save backups to Amazon S3.',
    author='Christian Giacomi, Thomas Skyttegaard Hansen, Hotboard.io (https://www.hotboard.io)',
    url='https://github.com/Hotboard/freeze',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'boto3',
        'click',
        'PyYAML',
        'simple-crypt'
    ],
    entry_points='''
        [console_scripts]
        freeze=freeze:cli
    ''',
)