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
  * [Installation and Usage](#installation-and-usage)
  * [Version control integration](#version-control-integration)
  * [Contributing](#contributing)
  * [FAQ](#faq)
    + [How do I use `blackbricks` on my Databricks notebooks?](#how-do-i-use--blackbricks--on-my-databricks-notebooks-)
    + [Is there a more streamlined way to do it?](#is-there-a-more-streamlined-way-to-do-it-)

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
    rev: 0.3.5
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

`blackbricks` is a command line program, meant to be used on files stored locally. Databricks provides no direct way to run tools on notebooks from within the notebook interface in your browser. 

The suggested way to use this is togheter with Git. 
1. Sync your notebooks to a remote repository (through the "revision history" tab in the top right)
2. Clone the repo locally
3. Run `blackbricks` on the desired notebook files from a terminal
4. Commit the newly formatted notebooks and push to your remote repo.
5. Sync your notebook again to pick up the new changes.

### Is there a more streamlined way to do it?

I'm considering adding an option to modify the Databricks notebooks directly (thorugh an additional commandline option). Something like
```
blackbricks --remote username:path/to/file  # Not possible (yet).
```
Click here to indicate interest, and enable watching this repo for new releases: 

[![](https://api.gh-polls.com/poll/01ED43J871S0Q1YSW2DFV3J8N9/Yes%2C%20please%20make%20a%20command%20line%20option%20for%20this%21)](https://api.gh-polls.com/poll/01ED43J871S0Q1YSW2DFV3J8N9/Yes%2C%20please%20make%20a%20command%20line%20option%20for%20this%21/vote)
[![](https://api.gh-polls.com/poll/01ED43J871S0Q1YSW2DFV3J8N9/I%20would%20rather%20pay%20for%20a%20Chrome%20extension.)](https://api.gh-polls.com/poll/01ED43J871S0Q1YSW2DFV3J8N9/I%20would%20rather%20pay%20for%20a%20Chrome%20extension./vote)
