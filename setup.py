import os
import ast

from setuptools import setup
from setuptools.command.test import test as TestCommand

VALUES = {
    '__version__': None,
    '__title__': None,
    '__description__': None
}

with open('slack_cli/__init__.py', 'r') as f:
    tree = ast.parse(f.read())
    for node in tree.body:
        if node.__class__ != ast.Assign:
            continue
        target = node.targets[0]
        if target.id in VALUES:
            VALUES[target.id] = node.value.s

if not all(VALUES.values()):
    raise RuntimeError("Can't locate values to init setuptools hook.")


version = VALUES['__version__']
project_name = 'slack-cli'
package_name = 'slack_cli'

project_url = 'http://github.com/rmotr/{project_name}'.format(
    project_name=project_name)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ["tests.py"]

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import sys
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def read_requirements(file_name):
    with open(file_name, 'r') as fp:
        return [l.strip() for l in fp if l.strip() and not l.startswith('-r')]


setup(
    name=VALUES['__title__'],
    version=version,
    description=VALUES['__description__'],
    url=project_url,
    download_url="{url}/tarball/{version}".format(
        url=project_url, version=version),
    author='Santiago Basulto',
    author_email='santiago@rmotr.com',
    license='MIT',
    scripts=['main.py'],
    packages=[package_name],
    maintainer='Santiago Basulto',
    install_requires=read_requirements('requirements.txt'),
    tests_require=read_requirements('dev-requirements.txt'),
    entry_points={
        'console_scripts': [
            'slack = main:main'
        ]
    },
    zip_safe=True,
    cmdclass={'test': PyTest},
)
