# Changelog

All notable changes to `xknx-catalog` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2026-09-12)


### Features

* **knx-gui:** rename Manufacturer section to Metadata, add full device metadata ([#28](https://github.com/XKNX/xknxtoolkit/issues/28)) ([ab3210b](https://github.com/XKNX/xknxtoolkit/commit/ab3210be1a3aedb9c9712371215d28e96bf202fb))
* **knx-gui:** show manufacturer and application human-readable names ([#27](https://github.com/XKNX/xknxtoolkit/issues/27)) ([2960485](https://github.com/XKNX/xknxtoolkit/commit/29604855ca1a6c87668a6a4b8cb7efdc3d910695))


### Documentation

* mark all changelogs unreleased, add changelog-format CI check ([#3](https://github.com/XKNX/xknxtoolkit/issues/3)) ([08ae6ef](https://github.com/XKNX/xknxtoolkit/commit/08ae6ef90e972bf99dd73d685f091b2326064d51))

## [Unreleased]

### Added

- REST API for browsing and querying the KNX product catalog.
- OpenAPI schema export via `export-openapi` entry point.
- Integration with `xknx-product` for `.knxprod` archive ingestion.
