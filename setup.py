from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="tinystream",
    description="Yet another python streams library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="0.1.14",
    url="https://github.com/mreiche/python-streams",
    author="Mike Reiche",
    py_modules=['tinystream'],
    install_requires=[],
)
