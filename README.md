## Detecting Outliers in Premise Operations (dopo)

[![PyPI](https://img.shields.io/pypi/v/dopo.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/dopo.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/dopo)][pypi status]
[![License](https://img.shields.io/pypi/l/dopo)][license]


[pypi status]: https://pypi.org/project/dopo/

## About dopo

The **Premise Validation Project** introduces the Python package `dopo`
(**D**etecting **O**utliers in **P**remise **O**perations), a toolkit 
for evaluating the consistency of background life cycle inventories and 
identifying anomalies that could affect LCA results.

It is essentially a wrapper around the [Brightway2](https://brightway.dev/) ``bw2analyzer`` library,
combined with a Dash web application for interactive exploration of datasets and results.

---

## 🧪 Features

- Detect structural and numerical outliers in ecoinvent-based inventories.
- Interface with Brightway2 and Premise-modified databases.
- Filter or classify activities based on CPC, ISIC, or custom sector definitions.
- Assess differences in environmental impacts from method-to-method or database-to-database.

---

## 📊 Dash Web Application

`dopo` includes a Dash-based interactive app for exploring datasets and visualizing environmental impact scores across projects.

### App Features

- ✅ Load and switch between multiple Brightway projects
- ✅ Select one or more background databases
- ✅ Choose a dataset grouping: **Sectors**, **CPC**, or **ISIC**
- ✅ Filter datasets with a search bar
- ✅ (Optional) Exclude market activities using a checkbox
- ✅ Select one or more impact assessment methods
- ✅ View either total impact scores or contribution plots
- ✅ Interactive dropdowns to explore results by sector and method
- ✅ Run calculations and visualize scores in seconds

## Installation

> [!IMPORTANT]
> You need to install ``dopo`` in a Python environment with `brightway` (2 or 2.5).

You can install _dopo_ via from Anaconda:

```console
$ conda install romainsacchi::dopo
```

Or via [pip] from [PyPI]:

```console
$ pip install dopo
```

> [!IMPORTANT]
> For Mac users with an ARM chip, you need to have `scikit-umfpack` 
> as well as `numpy<=1.24.4`, otherwise it results in slow calculations.
> This is not specific to `dopo` but to `brightway` in general.

### How to run the app

You can launch the app directly from the terminal using the following command:

```bash
dopo-dash
```

## Documentation

https://dopo.readthedocs.io/en/latest/


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

[License]: https://github.com/Laboratory-for-Energy-Systems-Analysis/dopo/blob/main/LICENSE
[Contributor Guide]: https://github.com/Laboratory-for-Energy-Systems-Analysis/dopo/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/Laboratory-for-Energy-Systems-Analysis/dopo/issues

## Maintainers

- [Romain Sacchi](romain.sacchi@psi.ch), PSI
- [Caroline Friedberger](cafriedb@stud.ntnu.no), NTNU

## Support

Feel free to contact [Romain Sacchi](romain.sacchi@psi.ch) if 
you have any questions or need help.
