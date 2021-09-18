#!/usr/bin/python3
import os
from setuptools import setup


with open("./README.md", "r", encoding="utf8") as file:
    long_description = file.read()


setup(
    name="pep249",
    version="1.0.1",
    url="https://github.com/abersheeran/pep249",
    description="Provide minimum implementation check and connection pool of PEP249.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="abersheeran",
    author_email="me@abersheeran.com",
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    python_requires=">=3.7.0",
    py_modules=["pep249"],
)
