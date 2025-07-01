#!/usr/bin/env python3
"""
NetGrid - Network Interface Information Tool

A command line tool to provide visual tables of network interface information
including link state, IP addresses, MAC addresses, and vendor information.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="netgrid",
    version="0.1.0",
    description="Network Interface Information Tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="NetGrid Team",
    author_email="",
    url="https://github.com/yourusername/netgrid",
    packages=find_packages(where="src"),
    package_dir={"netgrid": "src/netgrid"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
    },
    entry_points={
        "console_scripts": [
            "netgrid=netgrid.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="network, interfaces, monitoring, cli, linux",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/netgrid/issues",
        "Source": "https://github.com/yourusername/netgrid",
        "Documentation": "https://netgrid.readthedocs.io/",
    },
) 