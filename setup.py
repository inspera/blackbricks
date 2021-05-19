from pathlib import Path

from setuptools import setup, find_packages

from version import get_version

CURRENT_DIR = Path(__file__).parent


def get_long_description():
    readme_md = CURRENT_DIR / "README.md"
    with open(readme_md) as ld_file:
        return ld_file.read()


setup(
    name="blackbricks",
    description="Black for Databricks notebooks",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    keywords="automation formatter black sql yapf autopep8 pyfmt gofmt rustfmt",
    author="Bendik Samseth",
    author_email="bendik.samseth@inspera.no",
    url="https://github.com/inspera/blackbricks",
    license="MIT",
    python_requires=">=3.6",
    install_requires=[
        "black>=21.5b1",
        "sqlparse>=0.3.1",
        "databricks-cli>=0.11.0",
        "typer>=0.3.0",
        "colorama>=0.4.3",
    ],
    packages=find_packages(),
    version=get_version(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Quality Assurance",
    ],
    entry_points={"console_scripts": ["blackbricks=blackbricks.cli:app"]},
)
