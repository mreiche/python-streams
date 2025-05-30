import os
from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = os.environ.get("PACKAGE_VERSION", "0.0.1")

setup(
    name="tinystream",
    description="Yet another python streams library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=VERSION,
    url="https://github.com/mreiche/python-streams",
    author="Mike Reiche",
    py_modules=['tinystream'],
    install_requires=[],
)
