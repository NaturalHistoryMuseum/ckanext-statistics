# ckanext-statistics

#### API for accessing Natural History Museum Data Portal statistics.

# API Endpoint

### Downloads

```
http://data.nhm.ac.uk/api/3/action/download_statistics
```

Displays number of download events & records downloaded for the collections, research and GBIF datasets.

#### Parameters

Download statistics be filtered by year (YYYY) and month (MM).

```
http://data.nhm.ac.uk/api/3/action/download_statistics?year=2017&month=08
```

### Dataset

Provides count of 

# Commands

GBIF Download statistics are collected by running command:

```python
paster --plugin=ckanext-statistics statistics gbif -c /etc/ckan/default/development.ini
```

This is run daily on CRON.

# TODO: 

Run on cron