<img src=".github/nhm-logo.svg" align="left" width="150px" height="100px" hspace="40"/>

# ckanext-statistics

[![Travis](https://img.shields.io/travis/NaturalHistoryMuseum/ckanext-statistics/master.svg?style=flat-square)](https://travis-ci.org/NaturalHistoryMuseum/ckanext-statistics)
[![Coveralls](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-statistics/master.svg?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-statistics)
[![CKAN](https://img.shields.io/badge/ckan-2.9.0a-orange.svg?style=flat-square)](https://github.com/ckan/ckan)

_A CKAN extension for accessing instance statistics._


# Overview

Shows statistics for datasets and downloads on the CKAN instance.

**NB**: This extension currently only works with the Natural History Museum's theme extension [ckanext-nhm](https://github.com/NaturalHistoryMuseum/ckanext-nhm).


# Installation

Path variables used below:
- `$INSTALL_FOLDER` (i.e. where CKAN is installed), e.g. `/usr/lib/ckan/default`
- `$CONFIG_FILE`, e.g. `/etc/ckan/default/development.ini`

1. Clone the repository into the `src` folder:

  ```bash
  cd $INSTALL_FOLDER/src
  git clone https://github.com/NaturalHistoryMuseum/ckanext-statistics.git
  ```

2. Activate the virtual env:

  ```bash
  . $INSTALL_FOLDER/bin/activate
  ```

3. Install the requirements from requirements.txt:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-statistics
  pip install -r requirements.txt
  ```

4. Run setup.py:

  ```bash
  cd $INSTALL_FOLDER/src/ckanext-statistics
  python setup.py develop
  ```

5. Add 'statistics' to the list of plugins in your `$CONFIG_FILE`:

  ```ini
  ckan.plugins = ... statistics
  ```

# Configuration

These are no configuration options for this extension.


# Usage

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

1. `gbif`: retrieve download statistics from [GBIF](https://gbif.org).
    ```bash
    paster --plugin=ckanext-statistics statistics gbif -c $CONFIG_FILE
    ```


# Testing

_Test coverage is currently extremely limited._

To run the tests, use nosetests inside your virtualenv. The `--nocapture` flag will allow you to see the debug statements.
```bash
nosetests --ckan --with-pylons=$TEST_CONFIG_FILE --where=$INSTALL_FOLDER/src/ckanext-statistics --nologcapture --nocapture
```
