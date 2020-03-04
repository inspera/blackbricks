"""
Gets the current version number from the most recent tag.

This will simply get the most recent tag name that , assuming this to be
in the proper version format

Use as:

    from version import *
    setup(
        ...
        version=get_version(),
        ...
    )
"""

__all__ = "get_version"

import subprocess


def get_version():

    # Get the version using "git describe".
    cmd = "git describe --tags".split()
    try:
        return subprocess.check_output(cmd).decode().strip()
    except subprocess.CalledProcessError:
        print("Unable to get version number from git tags")
        return "0.0.0"


if __name__ == "__main__":
    print(get_version())
