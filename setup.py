import codecs
import os
import re

import setuptools


NAME = "miniflask"
PACKAGES = setuptools.find_packages(where="src")
META_PATH = os.path.join("src", NAME, "__init__.py")
KEYWORDS = [NAME, "plugin-engine", "plugin-system"]
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "Environment :: Console",
    "Operating System :: MacOS",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Unix",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
INSTALL_REQUIRES = [
    "colored"
]
HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__\s+=\s+['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


if __name__ == "__main__":
    setuptools.setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=find_meta("url"),
        version=find_meta("version"),
        author=find_meta("author"),
        maintainer=find_meta("author"),
        long_description=read("README.md"),
        long_description_content_type="text/markdown",
        packages=PACKAGES,
        package_dir={"": "src"},
        classifiers=CLASSIFIERS,
        keywords=KEYWORDS,
        install_requires=INSTALL_REQUIRES,
        python_requires='>=3.6',
    )
