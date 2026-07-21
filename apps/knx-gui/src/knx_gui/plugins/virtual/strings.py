"""Virtual plugin strings."""

from pathlib import Path

from knx_gui.strings import BaseStrings, create_translator

_locale_dir = Path(__file__).parent / "locales"
_ = create_translator("virtual", _locale_dir)


class VirtualStrings(BaseStrings):
    @property
    def PANEL_VIRTUAL(self) -> str:
        return _("Virtual")

    @property
    def SECTION_ROUTER(self) -> str:
        return _("Virtual Router")

    @property
    def SECTION_DEVICES(self) -> str:
        return _("Virtual Devices")

    @property
    def LABEL_NAME(self) -> str:
        return _("Name")

    @property
    def LABEL_PORT(self) -> str:
        return _("Port")

    @property
    def LABEL_MULTICAST_GROUP(self) -> str:
        return _("Multicast")

    @property
    def BTN_START(self) -> str:
        return _("Start")

    @property
    def BTN_STOP(self) -> str:
        return _("Stop")

    @property
    def STATUS_STOPPED(self) -> str:
        return _("Stopped")

    @property
    def STATUS_STARTING(self) -> str:
        return _("Starting...")

    @property
    def STATUS_RUNNING(self) -> str:
        return _("Running")

    @property
    def STATUS_ERROR(self) -> str:
        return _("Error")

    @property
    def LABEL_SERIAL_NUMBER(self) -> str:
        return _("Serial Number")

    @property
    def LABEL_PROGRAMMING_MODE(self) -> str:
        return _("Programming Mode")

    @property
    def STATUS_PROGRAMMING_MODE(self) -> str:
        return _("Waiting for ETS...")


S = VirtualStrings()
