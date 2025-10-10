"""
Setup script for SQLL Client Library        

This script handles the installation and distribution of the SQLL Client Library.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Simple SQL Client Library for Python"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="sqll",
    version="1.0.0",
    author="Nana Adjei Manu",
    author_email="n.k.a.manu@gmail.com",
    description="A clean, intuitive SQL client library for Python with SQLite support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/claeusdev/sqll",
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database :: Database Engines/Servers",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=3.0.0",
            "sphinx-rtd-theme>=0.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sql-client=sqll.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="sqlite sql database client library python",
    project_urls={
        "Bug Reports": "https://github.com/claeusdev/sqll/issues",
        "Source": "https://github.com/claeusdev/sqll",
        "Documentation": "https://sqll.readthedocs.io/",
    },
)