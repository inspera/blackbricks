import re
import os


def get_version():
    """Return the current version number from blackbricks/__init__.py"""

    with open(os.path.join(os.path.dirname(__file__), "blackbricks/__init__.py")) as f:
        match = re.search(r'__version__ = "([0-9\.]+)"', f.read())
        assert match, "No version in blackbricks/__init__.py !"
        return match.group(1)


if __name__ == "__main__":
    print(get_version())
