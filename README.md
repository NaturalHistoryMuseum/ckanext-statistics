<!--header-start-->
<img src=".github/nhm-logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-statistics

[![Tests](https://img.shields.io/github/workflow/status/NaturalHistoryMuseum/ckanext-statistics/Tests?style=flat-square)](https://github.com/NaturalHistoryMuseum/ckanext-statistics/actions/workflows/main.yml)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-statistics/main?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-statistics)
[![CKAN](https://img.shields.io/badge/ckan-2.9.7-orange.svg?style=flat-square)](https://github.com/ckan/ckan)
[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue.svg?style=flat-square)](https://www.python.org/)
[![Docs](https://img.shields.io/readthedocs/ckanext-statistics?style=flat-square)](https://ckanext-statistics.readthedocs.io)

_A CKAN extension for accessing instance statistics._

<!--header-end-->

# Overview

<!--overview-start-->
Shows statistics for datasets and downloads on the CKAN instance.

**NB**: This extension currently only works with the Natural History Museum's theme extension [ckanext-nhm](https://github.com/NaturalHistoryMuseum/ckanext-nhm).

<!--overview-end-->

# Installation

<!--installation-start-->
Path variables used below:
- `$INSTALL_FOLDER` (i.e. where CKAN is installed), e.g. `/usr/lib/ckan/default`
- `$CONFIG_FILE`, e.g. `/etc/ckan/default/development.ini`

## Installing from PyPI

```shell
pip install ckanext-statistics
```

## Installing from source

1. Clone the repository into the `src` folder:
   ```shell
   cd $INSTALL_FOLDER/src
   git clone https://github.com/NaturalHistoryMuseum/ckanext-statistics.git
   ```

2. Activate the virtual env:
   ```shell
   . $INSTALL_FOLDER/bin/activate
   ```

3. Install via pip:
   ```shell
   pip install $INSTALL_FOLDER/src/ckanext-statistics
   ```

### Installing in editable mode

Installing from a `pyproject.toml` in editable mode (i.e. `pip install -e`) requires `setuptools>=64`; however, CKAN 2.9 requires `setuptools==44.1.0`. See [our CKAN fork](https://github.com/NaturalHistoryMuseum/ckan) for a version of v2.9 that uses an updated setuptools if this functionality is something you need.

## Post-install setup

1. Add 'statistics' to the list of plugins in your `$CONFIG_FILE`:
   ```ini
   ckan.plugins = ... statistics
   ```

<!--installation-end-->

# Configuration

<!--configuration-start-->
These are no configuration options for this extension.

<!--configuration-end-->

# Usage

<!--usage-start-->
## Actions

### `download_statistics`
Statistics for downloads of datasets from the instance.

```python
from ckan.plugins import toolkit

# all of these filters are optional
data_dict = {
                'resource_id': RESOURCE_ID,
                'year': YEAR,
                'month': MONTH
            }

toolkit.get_action('download_statistics')(
    context,
    data_dict
)
```

### `dataset_statistics`
Statistics for dataset records.

```python
from ckan.plugins import toolkit

# these filters are optional
data_dict = {
                'resource_id': RESOURCE_ID,
            }

toolkit.get_action('dataset_statistics')(
    context,
    data_dict
)
```

## Commands

### `statistics`

1. `initdb`: initialise the database model
   ```bash
    ckan -c $CONFIG_FILE statistics initdb
   ```

2. `gbif`: retrieve download statistics from [GBIF](https://gbif.org).
    ```bash
    ckan -c $CONFIG_FILE statistics gbif
    ```

<!--usage-end-->

# Testing

<!--testing-start-->
There is a Docker compose configuration available in this repository to make it easier to run tests. The ckan image uses the Dockerfile in the `docker/` folder.

To run the tests against ckan 2.9.x on Python3:

1. Build the required images:
   ```shell
   docker-compose build
   ```

2. Then run the tests.
   The root of the repository is mounted into the ckan container as a volume by the Docker compose
   configuration, so you should only need to rebuild the ckan image if you change the extension's
   dependencies.
   ```shell
   docker-compose run ckan
   ```

<!--testing-end-->
