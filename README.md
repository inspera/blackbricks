[![PyPI version](https://img.shields.io/pypi/v/blackbricks.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/blackbricks/)
[![PyPI downloads](https://img.shields.io/pypi/dm/blackbricks)](https://pypistats.org/packages/blackbricks)
[![License](https://img.shields.io/pypi/l/blackbricks)](LICENSE)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Blackbricks

A formatting tool for your Databricks notebooks.

- Python cells are formatted with [black](https://github.com/psf/black)
- SQL cells are formatted with [sqlparse](https://github.com/andialbrecht/sqlparse)

## Table of Contents
- [Blackbricks](#blackbricks)
  * [Installation](#installation)
  * [Usage](#usage)
  * [Version control integration](#version-control-integration)
  * [Contributing](#contributing)
  * [FAQ](#faq)
    + [How do I use `blackbricks` on my Databricks notebooks?](#how-do-i-use--blackbricks--on-my-databricks-notebooks-)

## Installation

Install:

```bash
$ pip install blackbricks
```

You probably also want to have installed the `databricks-cli`, in order to use `blackbricks` directly on your notebooks.

``` bash
$ pip install databricks-cli
$ databricks configure  # Required in order to use `blackbricks` on remote notebooks.
```

## Usage
You can use `blackbricks` on Python notebook files stored locally, or directly on the notebooks stored in Databricks. 

For the most part, `blackbricks` operates very similary to `black`.

``` bash
$ blackbricks notebook1.py notebook2.py # Formats both notebooks.
$ blackbricks notebook_directory/ # Formats every notebook under the directory (recursively).
```
An important difference is that `blackbricks` will ignore any file that does not contain the `# Databricks notebook source` header on the first line. Databricks adds this line to all Python notebooks. This means you can happily run `blackbricks` on a directory with both notebooks and regular Python files, and `blackbricks` won't touch the latter.

If you specify the `-r` or `--remote` flag, `blackbricks` will work directly on your notebooks stored in Databricks.

``` bash
$ blackbricks --remote /Users/username/notebook.py
```

When working on remote files, you _can not_ add whole directories.

### Full usage

```text
$ blackbricks --help
Usage: blackbricks [OPTIONS] [FILENAMES]...

  Formatting tool for Databricks python notebooks.

  Python cells are formatted using `black`, and SQL cells are formatted by
  `sqlparse`.

  Local files (without the `--remote` option):

    - Only files that look like Databricks (Python) notebooks will be
    processed. That is, they must start with the header `# Databricks
    notebook source`

    - If you specify a directory as one of the file names, all files in that
    directory will be added, including any subdirectory.

  Remote files (with the `--remote` option):

    - Make sure you have installed the Databricks CLI (``pip install
    databricks_cli``)

    - Make sure you have configured at least one profile (`databricks
    configure`). Check the file `~/.databrickscfg` if you are not sure.

    - File paths should start with `/`. Otherwise they are interpreted as
    relative to `/Users/username`, where `username` is the username
    specified in the Databricks profile used.

Arguments:
  [FILENAMES]...  Path to the notebook(s) to format.

Options:
  -r, --remote                    If this option is used, all filenames are
                                  treated as paths to notebooks on your
                                  Databricks host (i.e. not local files).
                                  [default: False]

  -p, --profile NAME              If using --remote, which Databricks profile
                                  to use.  [default: DEFAULT]

  --line-length INTEGER           How many characters per line to allow.
                                  [default: 88]

  --sql-upper / --no-sql-upper    SQL keywords should be UPPERCASE or
                                  lowercase.  [default: True]

  --indent-with-two-spaces / --no-indent-with-two-spaces
                                  Use two spaces for indentation in Python
                                  cells instead of Black's default of four.
                                  Databricks uses two spaces.  [default: True]

  --check                         Don't write the files back, just return the
                                  status. Return code 0 means nothing would
                                  change.

  --diff                          Don't write the files back, just output a
                                  diff for each file on stdout.

  --version                       Display version information and exit.
  --help                          Show this message and exit.
```



## Version control integration

Use [pre-commit](https://pre-commit.com). Add a `.pre-commit-config.yaml` file
to your repo with the following content (changing/removing the `args` as you
wish): 

```yaml
repos:
-   repo: https://github.com/bsamseth/blackbricks
    rev: 0.4.0
    hooks:
    - id: blackbricks
      args: [--line-length=120, --indent-with-two-spaces]
```

Set the `rev` attribute to the most recent version of `blackbricks`.
The `args` are optional and can be used to set any of `blackbricks` options.

## Contributing

If you find blackbricks useful or utterly broken, you are more than welcome to contribute improvements. Please open an issue first to discuss what you want added/fixed. Unless you are just adding tests. In that case your pull request is extremely likely to be merged right away.

## FAQ

### How do I use `blackbricks` on my Databricks notebooks?

First, make sure you have set up `databricks-cli` on your system (see
[installation](#installation)), and that you have at least one profile setup in
`~/.databrickscfg`. As an example:

``` toml
# File: ~/.databrickscfg

[DEFAULT]
host = https://dbc-123456-a1243.cloud.databricks.com/
username = username@example.com
password = dapi12345678901234567890

[OTHERPROFILE]
host = https://dbc-654321-1234.cloud.databricks.com
username = name.user@example.com
password = dapi09876543211234567890
```

You can then do:

``` bash
$ blackbricks --remote /Users/username@example.com/notebook.py  # Uses DEFAULT profile.
$ blackbricks --remote notebook.py  # Equivalent to the above.
$ blackbricks --remote --profile OTHERPROFILE /Users/name.user@example.com/notebook.py
$ blackbricks --remote --profile OTHERPROFILE notebook.py  # Equivalent to the above.
```

