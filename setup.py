#!/usr/bin/env python
"""Setup script for smart-coach-pose-estimation package.

This file provides backward compatibility for older pip versions.
For modern installations, pyproject.toml is used.
"""

from setuptools import setup

# Read the contents of README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="smart-coach-pose-estimation",
    use_scm_version=False,
    long_description=long_description,
    long_description_content_type="text/markdown",
)
