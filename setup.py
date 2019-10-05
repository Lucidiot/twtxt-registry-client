#!/usr/bin/env python3
from typing import List
from setuptools import setup, find_packages


def read_requirements(filename: str) -> List[str]:
    return [req.strip() for req in open(filename)]


requirements = read_requirements('requirements.txt')
dev_requirements = read_requirements('requirements-dev.txt')

setup(
    name='twtxt-registry-client',
    version=open('VERSION').read().strip(),
    author='Lucidiot',
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"],
    ),
    entry_points={
        'console_scripts': [
            'twtxt-registry=twtxt_registry_client.__main__:cli',
        ],
    },
    package_data={
        '': ['LICENSE', 'README', 'README.rst'],
    },
    python_requires='>=3.5',
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
    },
    license='GNU General Public License 3',
    description="API client for twtxt registries",
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    keywords="twtxt twitter registry twtxt-registry client",
    url="https://gitlab.com/Lucidiot/twtxt-registry-client",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Communications",
        "Topic :: Utilities",
    ],
    project_urls={
        "Source Code": "https://gitlab.com/Lucidiot/twtxt-registry-client",
        "GitHub Mirror": "https://github.com/Lucidiot/twtxt-registry-client",
    }
)
