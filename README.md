[![PyPI version](https://img.shields.io/pypi/v/blackbricks.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/blackbricks/)
[![PyPI downloads](https://img.shields.io/pypi/dm/blackbricks)](https://pypistats.org/packages/blackbricks)
[![License](https://img.shields.io/pypi/l/blackbricks)](LICENSE)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Blackbricks

A formatting tool for your Databricks notebooks.

- Python cells are formatted with [black](https://github.com/psf/black)
- SQL cells are formatted with [sqlparse](https://github.com/andialbrecht/sqlparse)

## Installation and Usage

Install:

```bash
$ pip install blackbricks
```

Usage:

```text
$ blackbricks --help
usage: blackbricks [-h] [--line-length LINE_LENGTH]
                   [--sql-upper | --sql-lower] [--check | --diff]
                   [--indent-with-two-spaces] [--version]
                   [filenames [filenames ...]]

Formatting tool for Databricks python notebooks. Python cells are formatted
using `black`, and SQL cells are formatted by `sqlparse`.

positional arguments:
  filenames             Path to the notebook(s) to format

optional arguments:
  -h, --help            show this help message and exit
  --line-length LINE_LENGTH
                        How many characters per line to allow. [default: ask
                        black]
  --sql-upper           SQL keywords should be uppercase
  --sql-lower           SQL keywords should be lowercase
  --check               Don't write the files back, just return the status.
                        Return code 0 means nothing would change.
  --diff                Don't write the files back, just output a diff for
                        each file on stdout
  --indent-with-two-spaces
                        Use two spaces for indentation in Python cells instead
                        of Black's default of four.
  --version             Display version information and exit.
```


## Version control integration

Use [pre-commit](https://pre-commit.com). Add a
`.pre-commit-config.yaml` file to your repo with the following content (changing/removing the `args` as you wish):

```yaml
repos:
-   repo: https://github.com/bsamseth/blackbricks
    rev: 0.3.4
    hooks:
    - id: blackbricks
      args: [--line-length=120, --indent-with-two-spaces]
```

Set the `rev` attribute to the most recent version of `blackbricks`.
The `args` are optional and can be used to set any of `blackbricks` options.

## Contributing

If you find blackbricks useful or utterly broken, you are more than welcome to contribute improvements. Please open an issue first to discuss what you want added/fixed. Unless you are just adding tests. In that case your pull request is extremely likely to be merged right away.
