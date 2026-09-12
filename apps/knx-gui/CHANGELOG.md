# Changelog

All notable changes to `knx-gui` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2026-09-12)


### Features

* **knx-gui:** add a bottom status bar for background tasks ([#36](https://github.com/XKNX/xknxtoolkit/issues/36)) ([ac577ad](https://github.com/XKNX/xknxtoolkit/commit/ac577ad609307fdfece0e4907fc059af7f1b7e8e))
* **knx-gui:** add a Program Device section with button/serial addressing ([#35](https://github.com/XKNX/xknxtoolkit/issues/35)) ([177a196](https://github.com/XKNX/xknxtoolkit/commit/177a196a5f88250965fc6af528c38ec065e59b00))
* **knx-gui:** add device restart / master reset UI ([#24](https://github.com/XKNX/xknxtoolkit/issues/24)) ([fe3f58e](https://github.com/XKNX/xknxtoolkit/commit/fe3f58e38fee66f38106b88611dccd3d021103cc))
* **knx-gui:** rename Manufacturer section to Metadata, add full device metadata ([#28](https://github.com/XKNX/xknxtoolkit/issues/28)) ([ab3210b](https://github.com/XKNX/xknxtoolkit/commit/ab3210be1a3aedb9c9712371215d28e96bf202fb))
* **knx-gui:** segmented Individual Address input, Area/Line/Device bounded ([#26](https://github.com/XKNX/xknxtoolkit/issues/26)) ([1ab42e3](https://github.com/XKNX/xknxtoolkit/commit/1ab42e3b20d5b6cdabdaed3eecd95d2924ba5502))
* **knx-gui:** show manufacturer and application human-readable names ([#27](https://github.com/XKNX/xknxtoolkit/issues/27)) ([2960485](https://github.com/XKNX/xknxtoolkit/commit/29604855ca1a6c87668a6a4b8cb7efdc3d910695))


### Bug Fixes

* import block sort in knx-gui test_device.py ([#46](https://github.com/XKNX/xknxtoolkit/issues/46)) ([9e24791](https://github.com/XKNX/xknxtoolkit/commit/9e2479138dc75d69446c944e454e64fad6645f2a))
* **knx-gui:** repaint during window resize instead of freezing ([#34](https://github.com/XKNX/xknxtoolkit/issues/34)) ([3e179d0](https://github.com/XKNX/xknxtoolkit/commit/3e179d009b2749d57a376824fd47ec8b583defc4))
* **product:** raise EncodingError on corrupt encode data instead of silent skips ([#55](https://github.com/XKNX/xknxtoolkit/issues/55)) ([c6e3aa8](https://github.com/XKNX/xknxtoolkit/commit/c6e3aa83099bdb1493a30c6b0232516080d9a475))


### Documentation

* mark all changelogs unreleased, add changelog-format CI check ([#3](https://github.com/XKNX/xknxtoolkit/issues/3)) ([08ae6ef](https://github.com/XKNX/xknxtoolkit/commit/08ae6ef90e972bf99dd73d685f091b2326064d51))

## [Unreleased]

### Added

- Node-based project editor for devices and group addresses.
- Product catalog browser, backed by `xknx-catalog`.
- Real KNX connections over tunneling and routing, plus virtual devices and a proxy for testing without hardware.
- Network monitor and structured application logs.
