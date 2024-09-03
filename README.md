# premise_validation

[![PyPI](https://img.shields.io/pypi/v/premise_validation.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/premise_validation.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/premise_validation)][pypi status]
[![License](https://img.shields.io/pypi/l/premise_validation)][license]

[![Read the documentation at https://premise_validation.readthedocs.io/](https://img.shields.io/readthedocs/premise_validation/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/cafriedb/premise_validation/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/cafriedb/premise_validation/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/premise_validation/
[read the docs]: https://premise_validation.readthedocs.io/
[tests]: https://github.com/cafriedb/premise_validation/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/cafriedb/premise_validation
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## About the Project
The premise validation project developed the python package "dopo" (short for: Detecting Outliers in Premise Operations). The package provides a first outlier detection framework for premise based prospective-lca databases.
It visualizes a premise database by sector and compares it to the inital ecoinvent database. Currently dopo creates three kinds of plots which give the user information on different granularity levels and tables containing corresponding information. The visualization is done in excel workbooks. Dopo is to support faster outlier detection to better understand premise data and based results.

## Installation

You can install _dopo_ via [pip] from [PyPI]:

```console
$ pip install dopo
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [MIT license][License],
_dopo_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://premise_validation.readthedocs.io/en/latest/usage.html
[License]: https://github.com/cafriedb/premise_validation/blob/main/LICENSE
[Contributor Guide]: https://github.com/cafriedb/premise_validation/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/cafriedb/premise_validation/issues


## Building the Documentation

You can build the documentation locally by installing the documentation Conda environment:

```bash
conda env create -f docs/environment.yml
```

activating the environment

```bash
conda activate sphinx_premise_validation
```

and [running the build command](https://www.sphinx-doc.org/en/master/man/sphinx-build.html#sphinx-build):

```bash
sphinx-build docs _build/html --builder=html --jobs=auto --write-all; open _build/html/index.html
```
