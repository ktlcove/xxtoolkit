import os

from setuptools import find_packages, setup

APP_VERSION = '0.0.1'

APP_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

APP_REQUIREMENTS = [
    'ruamel.yaml',
    'pytz',
    'attrs',
    'asyncpg',
    'starlette',
]

APP_DEPENDENCY_LINKS = []

APP_CONSOLE_SCRIPTS = []

setup(
    name=APP_NAME,
    version=APP_VERSION,
    classifiers=[
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python 3',
    ],
    packages=find_packages(),
    #     include_package_data=True,
    #     exclude_package_date={'': ['.gitignore']},
    entry_points={'console_scripts': APP_CONSOLE_SCRIPTS},
    install_requires=APP_REQUIREMENTS,
    dependency_links=APP_DEPENDENCY_LINKS,
)
