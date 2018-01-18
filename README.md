# ckanext-statistics

[![Travis branch](https://img.shields.io/travis/NaturalHistoryMuseum/ckanext-statistics/master.svg?style=flat-square)](https://travis-ci.org/NaturalHistoryMuseum/ckanext-statistics) [![Coveralls github branch](https://img.shields.io/coveralls/github/NaturalHistoryMuseum/ckanext-statistics/master.svg?style=flat-square)](https://coveralls.io/github/NaturalHistoryMuseum/ckanext-statistics)

#### API for accessing Natural History Museum Data Portal statistics.

# Download statistics API

```
http://data.nhm.ac.uk/api/3/action/download_statistics
```

Displays number of download events & records downloaded for the collections, research and GBIF datasets.

### Parameters:

Download statistics can be filtered by date.

* Year (YYYY)
* Month (MM)

```
http://data.nhm.ac.uk/api/3/action/download_statistics?year=2017&month=08
```

# Dataset statistics API

Provides total number of records across all datasets.

```
http://data.nhm.ac.uk/api/3/action/dataset_statistics
```

### API Parameters:

Dataset statistics can be filtered by resource ID.

* resource_id (UUID)

```
http://data.nhm.ac.uk/api/3/action/dataset_statistics?resource_id=05ff2255-c38a-40c9-b657-4ccb55ab2feb
```

# Commands

GBIF Download statistics are collected by a paster command:

```
paster --plugin=ckanext-statistics statistics gbif -c /etc/ckan/default/development.ini
```

This runs daily on CRON.

# TODO: 

* Set up GBIF stats command to run on cron.
* Dataset statistics - for collections datasets show changes over time using created field.
