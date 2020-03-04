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
```


## Version control integration

Use [pre-commit](https://github.com/andialbrecht/sqlparse). Add a
`.pre-commit-config.yaml` file to your repo with the following content:

```yaml
repos:
-   repo: https://github.com/bsamseth/blackbricks
    rev: 0.2.1
    hooks:
    - id: blackbricks
      args: [--line-length=120]
```

Set the `rev` attribute to the most recent version of `blackbricks`.
The `args` are optional and can be used to set any of `blackbricks` options.
