#encoding: utf-8
import io

from apidoc2runner import __version__
from setuptools import find_packages, setup

with io.open("README.md", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='apidoc2runner',
    version=__version__,
    description='Convert apidoc data to JSON testcases for HttpRunner.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='gerrywen',
    author_email='blog@gerrywen.com',
    url='https://github.com/gerrywen/apidoc2runner',
    license='MIT',
    packages=find_packages(exclude=['test.*', 'test']),
    package_data={},
    keywords='apidoc converter json',
    install_requires=[],
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    entry_points={
        'console_scripts': [
            'apidoc2runner=apidoc2runner.cli:main'
        ]
    }
)
