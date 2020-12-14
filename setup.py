# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 11:30:00 2020

@author: Ruben
"""

from setuptools import setup

setup_args = dict(
    name="humedadinso",
    version="0.1",
    url='http://github.com/isi-ies-group/humedadinso',
    author="Ruben",
    author_email="ruben.nunez@upm.es",
    description="humedad en modulos insolight",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Windows",
    ],
    python_requires='>=3.6',
    packages=['humedadinso'],
    zip_safe=False,
    package_data={'': ['*.txt','*.yaml']},
    include_package_data=True,
)

install_requires = [
    'pandas',
    'datetime',
    'matplotlib',
    'psychrochart',
    'psychrolib',
    'lectura_equipos',
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)

