# Changelog

## v4.0.0 (2025-07-08)

### Breaking Changes

- remove obsolete gbif download table model
- retrieve gbif download stats directly from their api

### Feature

- **gbif**: retrieve gbif download stats directly from their api

### Fix

- zero-pad month in gbif param

### Refactor

- **gbif**: remove obsolete gbif download table model
- use migration scripts to manage database

### Docs

- remove commands from readme
- update configuration options in readme

### Tests

- fix tests for gbif stat updates

## v3.1.15 (2025-06-09)

### Build System(s)

- update ckantools

### CI System(s)

- set ruff target py version, add more ignores - avoid using fixes that don't work for python 3.8 (our current version) - ignore recommended ruff formatter conflicts - ignore more docstring rules
- remove pylint, add ruff lint rules Primarily the defaults plus pydocstyle and isort.
- update pre-commit repo versions

## v3.1.14 (2025-05-06)

### Fix

- remove python1 reference in shebang
- catch validation errors when counting records

### Refactor

- remove dependency on ckanext-ckanpackager by copying its model

### Tests

- fix tests by removing ckanpackager instantiation

## v3.1.13 (2024-11-04)

### Docs

- use variable logo based on colour scheme
- fix tests badge tests workflow file was renamed

### Style

- automatic reformat auto reformat with ruff/docformatter/prettier after config changes

### Build System(s)

- remove version from docker compose file version specifier is deprecated

### CI System(s)

- fix python setup action version
- add merge to valid commit types
- add docformatter args and dependency docformatter currently can't read from pyproject.toml without tomli
- only apply auto-fixes in pre-commit F401 returns linting errors as well as auto-fixes, so this disables the errors and just applies the fixes
- update tool config update pre-commit repo versions and switch black to ruff
- add pull request validation workflow new workflow to check commit format and code style against pre-commit config
- update workflow files standardise format, change name of tests file

### Chores/Misc

- add pull request template
- update tool details in contributing guide

## v3.1.12 (2024-08-20)

### Chores/Misc

- add build section to read the docs config

## v3.1.11 (2023-11-23)

### Fix

- add zero if count is None

## v3.1.10 (2023-10-05)

### Build System(s)

- change version specifiers for nhm ckan extensions

## v3.1.9 (2023-10-03)

### Fix

- update minor version of vds

### Chores/Misc

- add regex for version line in citation file
- add citation.cff to list of files with version
- add contributing guidelines
- add code of conduct
- add citation file
- update support.md links

## v3.1.8 (2023-07-18)

### Tests

- add nav slugs table

### Build System(s)

- update dependencies

## v3.1.7 (2023-07-17)

### Docs

- update logos

## v3.1.6 (2023-04-11)

### Build System(s)

- fix postgres not loading when running tests in docker

### Chores/Misc

- add action to sync branches when commits are pushed to main

## v3.1.5 (2023-03-20)

### Build System(s)

- **deps**: bump vds version

## v3.1.4 (2023-02-20)

### Docs

- fix api docs generation script

### Chores/Misc

- small fixes to align with other extensions

## v3.1.3 (2023-02-06)

### Build System(s)

- bump vds version

## v3.1.2 (2023-01-31)

### Docs

- **readme**: change logo url from blob to raw

## v3.1.1 (2023-01-31)

### Docs

- **readme**: direct link to logo in readme
- **readme**: fix github actions badge

## v3.1.0 (2023-01-30)

### Fix

- **downloads**: switch versioned-datastore class

### Docs

- remove outdated bit of docstring

### Style

- remove all the unicode string markers

### Build System(s)

- **docker**: use 'latest' tag for test docker image

### Chores/Misc

- bump vds version
- merge in new changes from dev

## v3.0.3 (2022-12-14)

### Build System(s)

- update minor version of vds

## v3.0.2 (2022-12-12)

### Style

- change quotes in setup.py to single quotes

### Build System(s)

- **requirements**: use compatible release specifier for extensions
- include top-level data files
- add package data

## v3.0.1 (2022-12-01)

### Docs

- **readme**: format test section
- **readme**: update installation steps
- **readme**: update ckan patch version in header badge

## v3.0.0 (2022-11-28)

### Breaking Changes

- ckan extensions now installed from PyPI. version numbers will need to be updated before pushing to main.

### Fix

- fix version number

### Docs

- add section delimiters and include-markdown

### Style

- apply formatting

### Build System(s)

- **requirements**: update minor versions of ckan extensions
- set changelog generation to incremental
- pin minor versions of dependencies
- unpin ckanpackager and vds versions

### CI System(s)

- add cz-nhm dependency

### Chores/Misc

- use cz_nhm commitizen config
- improve commitizen message template
- standardise package files

## v2.0.15 (2022-10-03)

## v2.0.14 (2022-09-06)

## v2.0.13 (2022-08-30)

## v2.0.12 (2022-08-22)

## v2.0.11 (2022-08-08)

## v2.0.10 (2022-06-13)

## v2.0.9 (2022-05-23)

## v2.0.8 (2022-05-17)

## v2.0.7 (2022-05-03)

## v2.0.6 (2022-04-25)

## v2.0.5 (2022-03-28)

## v2.0.4 (2022-03-21)

## v2.0.3 (2022-03-14)

## v2.0.2 (2022-03-07)

## v2.0.1 (2021-03-11)

## v2.0.0 (2021-03-09)

## v1.0.0-alpha (2019-07-23)

## v0.0.3 (2019-04-08)

## v0.0.2 (2018-06-28)

## v0.0.1 (2017-11-08)
