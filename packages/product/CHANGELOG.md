# Changelog

All notable changes to `xknx-product` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2026-09-12)


### Bug Fixes

* **product:** raise EncodingError on corrupt encode data instead of silent skips ([#55](https://github.com/XKNX/xknxtoolkit/issues/55)) ([c6e3aa8](https://github.com/XKNX/xknxtoolkit/commit/c6e3aa83099bdb1493a30c6b0232516080d9a475))
* **product:** warn instead of silently zeroing an unencodable parameter ([#54](https://github.com/XKNX/xknxtoolkit/issues/54)) ([f6e5dd1](https://github.com/XKNX/xknxtoolkit/commit/f6e5dd1ab2bc193b918935f4d62547150dfa0725))


### Documentation

* mark all changelogs unreleased, add changelog-format CI check ([#3](https://github.com/XKNX/xknxtoolkit/issues/3)) ([08ae6ef](https://github.com/XKNX/xknxtoolkit/commit/08ae6ef90e972bf99dd73d685f091b2326064d51))

## [Unreleased]

### Added

- Read `.knxprod` archives (ZIP files) and validate their internal structure.
- Parse manufacturer, catalog, hardware, and application program XMLs via `xknx-models`.
- Typed access to product catalog metadata and application program definitions.
