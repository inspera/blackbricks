[![PyPI version](https://img.shields.io/pypi/v/blackbricks.svg?logo=pypi&logoColor=FFE873)](https://pypi.org/project/blackbricks/)
[![Downloads](https://pepy.tech/badge/blackbricks)](https://pepy.tech/project/blackbricks)
[![Downloads per month](https://pepy.tech/badge/blackbricks/month)](https://pepy.tech/project/blackbricks/month)
[![License](https://img.shields.io/pypi/l/blackbricks)](LICENSE)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Blackbricks

A formatting tool for your Databricks notebooks.

- Python cells are formatted with [black](https://github.com/psf/black)
- SQL cells are formatted with [sqlparse](https://github.com/andialbrecht/sqlparse)

## Table of Contents

* [Installation](#installation)
* [Usage](#usage)
* [Version control integration](#version-control-integration)
* [Contributing](#contributing)
* [FAQ](#faq)
* [Breaking changes](#breaking-changes)

## Installation

While you can use `pip` directly, you should prefer using [pipx](https://pypa.github.io/pipx/).

```bash
$ pipx install blackbricks
```

You probably also want to have installed the `databricks-cli`, in order to use `blackbricks` directly on your notebooks.

``` bash
$ pipx install databricks-cli
$ databricks configure  # Required in order to use `blackbricks` on remote notebooks.
```

## Usage
You can use `blackbricks` on Python notebook files stored locally, or directly on the notebooks stored in Databricks. 

For the most part, `blackbricks` operates very similarly to `black`.

``` bash
$ blackbricks notebook1.py notebook2.py  # Formats both notebooks.
$ blackbricks notebook_directory/  # Formats every notebook under the directory (recursively).
```
An important difference is that `blackbricks` will ignore any file that does not contain the `# Databricks notebook
source` header on the first line. Databricks adds this line to all Python notebooks. This means you can happily run
`blackbricks` on a directory with both notebooks and regular Python files, and `blackbricks` won't touch the latter.

If you specify the `-r` or `--remote` flag, `blackbricks` will work directly on your notebooks stored in Databricks.

``` bash
$ blackbricks --remote /Users/username/notebook.py
$ blackbricks --remote /Repos/username/repo-name/notebook.py
```

### Full usage

```text
$ poetry run blackbricks --help

 Usage: blackbricks [OPTIONS] [FILENAMES]...

 Formatting tool for Databricks python notebooks.
 Python cells are formatted using `black`, and SQL cells are formatted by `sqlparse`.
 Local files (without the `--remote` option):
 - Only files that look like Databricks (Python) notebooks will be processed. That is,
 they must start with the header `# Databricks notebook source`
 - If you specify a directory as one of the file names, all files in that directory will
 be added, including any subdirectory.
 Remote files (with the `--remote` option):
 - Make sure you have installed the Databricks CLI (``pip install databricks_cli``)
 - Make sure you have configured at least one profile (`databricks configure`). Check the
 file `~/.databrickscfg` if you are not sure.
 - File paths should start with `/`. Otherwise they are interpreted as relative to
 `/Users/username`, where `username` is the username specified in the Databricks profile
 used.

╭─ Arguments ────────────────────────────────────────────────────────────────────────────╮
│   filenames      [FILENAMES]...  Path to the notebook(s) to format. [default: None]    │
╰────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────╮
│ --remote                     -r                             If this option is used,    │
│                                                             all filenames are treated  │
│                                                             as paths to notebooks on   │
│                                                             your Databricks host (i.e. │
│                                                             not local files).          │
│ --profile                    -p                    NAME     If using --remote, which   │
│                                                             Databricks profile to use. │
│                                                             [default: DEFAULT]         │
│ --line-length                                      INTEGER  How many characters per    │
│                                                             line to allow.             │
│                                                             [default: 88]              │
│ --sql-upper                      --no-sql-upper             SQL keywords should be     │
│                                                             UPPERCASE or lowercase.    │
│                                                             [default: sql-upper]       │
│ --check                                                     Don't write the files      │
│                                                             back, just return the      │
│                                                             status. Return code 0      │
│                                                             means nothing would        │
│                                                             change.                    │
│ --diff                                                      Don't write the files      │
│                                                             back, just output a diff   │
│                                                             for each file on stdout.   │
│ --version                                                   Display version            │
│                                                             information and exit.      │
│ --help                                                      Show this message and      │
│                                                             exit.                      │
╰────────────────────────────────────────────────────────────────────────────────────────╯
```



## Version control integration

Use [pre-commit](https://pre-commit.com). Add a `.pre-commit-config.yaml` file
to your repo with the following content (changing/removing the `args` as you
wish): 

```yaml
repos:
-   repo: https://github.com/inspera/blackbricks
    rev: 1.0.0
    hooks:
    - id: blackbricks
      args: [--line-length=120]
```

Set the `rev` attribute to the most recent version of `blackbricks`.
The `args` are optional and can be used to set any of `blackbricks` options.

## Contributing

If you find blackbricks useful, feel free to say so with a star. If you think it is utterly broken, you are more than
welcome to contribute improvements. Please open an issue first to discuss what you want added/fixed. Unless you are just
adding tests. In that case your pull request is extremely likely to be merged right away.

## FAQ

### Can I disable SQL formatting?

Sure! Certain SQL statements might not be parsed and indented properly by `sqlparse`, and the result can be jumbled
formatting. You can disable SQL formatting for a cell by adding `-- nofmt` to the very first line of a cell:

```sql
%sql  -- nofmt
select this,
             sql_will,   -- be kept just
         like_this
  from if_that_is.what_you_need
```

### How do I use `blackbricks` on my Databricks notebooks?

First, make sure you have set up `databricks-cli` on your system (see [installation](#installation)), and that you have
at least one profile setup in `~/.databrickscfg`. As an example:

```cfg
# File: ~/.databrickscfg

[DEFAULT]
host = https://dbc-b23456-a1243.cloud.databricks.com/
username = username@example.com
password = dapi12345678901234567890

[OTHERPROFILE]
host = https://dbc-c54321-d234.cloud.databricks.com
username = name.user@example.com
password = dapi09876543211234567890
```

You should use [access tokens](https://docs.databricks.com/dev-tools/api/latest/authentication.html) instead of your actual password.

You can then do:

``` bash
$ blackbricks --remote /Users/username@example.com/notebook.py  # Uses DEFAULT profile.
$ blackbricks --remote notebook.py  # Equivalent to the above.
$ blackbricks --remote --profile OTHERPROFILE /Users/name.user@example.com/notebook.py
$ blackbricks --remote --profile OTHERPROFILE notebook.py  # Equivalent to the above.
$ blackbricks --remote /Repos/username@example.com/repo-name/notebook.py  # Targeting notebook in a Repo
```

### Can you run blackbricks while using Databricks in the browser?

No. See https://github.com/inspera/blackbricks/issues/27 for why.

However, Databricks now allows you to [format your notebooks with black directly](https://docs.databricks.com/notebooks/notebooks-use.html#format-code-cells).

### I get an error: `TypeError: init() got an unexpected keyword argument 'no_args_is_help'`

This means you had an old version of `click` installed from before, and your installation didn't upgrade it
automatically. Updating your installation should do the trick, e.g. `pip install -U blackbricks` or similar depending on
your installation method of choice.


### Shell commands like `!ls` throws an error

See https://github.com/inspera/blackbricks/issues/21.

## Breaking changes

### Version policy

Style choices made by `blackbricks` will follow semantic versioning, with changes that cause differences resulting in
new major versions. Such changes will be kept to an absolute minimum, with none currently planned.

Style choices made by `black` (responsible for 95% of the formatting in a notebook) will not follow the same strict
semantic versioning. This is because `black` itself does not use semver, but instead provide a [year-based
policy](https://black.readthedocs.io/en/stable/the_black_code_style/index.html#stability-policy). `blackbricks` will
make a _minor_ version increase when it upgrades black to a new year. Such a bump should be made once the new year's
release of `black` is available. Feel free to open an issue if this has not been done yet. 

### Breaking changes with version 2.0

Notebooks will be terminated with a `\n` starting with version `2.0.0`. This harmonizes EOF handling and should be much
less annoying in practice than prior versions. This causes a diff on _any_ notebook that was previously formatted with
`blackbricks<2.0.0`.

Also, the deprecated and non-functional flag for two space indentation is removed, and providing said flag is now an error.

### Breaking changes with version 1.0

Earlier versions of blackbricks applied a patched version of black in order to allow two-space indentation. This was
done because Databricks used two-space indentation, and did not allow you to change that. 

Since then, Databricks has added the option to choose. Because you can now choose, blackbricks re-joins black in being
uncompromising, and since version 1.0 you can no longer choose anything but 4 space indentation.

If you _must_ keep using two-space indentation, then stick to versions `<1.0`.
