#!/usr/bin/env python3
"""Setup script for the Voice Dictation Tool."""

import os

from setuptools import find_packages, setup

# Read the README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="multi-dictate",
    version="1.0.0",
    author="Costa Shulyupin",
    author_email="constantine.shulyupin@gmail.com",
    description="A multi-language voice dictation application for Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/makelinux/multi-dictate",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "multi-dictate=multi_dictate.dictate:main",
        ],
    },
    package_data={
        "multi_dictate": ["*.yaml"],
    },
    data_files=[
        ("share/multi-dictate/model", []),  # We'll handle model files separately
    ],
    include_package_data=True,
)
