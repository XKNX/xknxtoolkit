from knx_gui.dpt import (
    DPT_BOOL,
    DPT_DIMMING,
    DPT_OPEN_CLOSE,
    DPT_PERCENT,
    DPT_RGB,
    DPT_SCENE,
    DPT_STOP,
    DPT_SWITCH,
    DPT_TEMPERATURE,
    DPT_UP_DOWN,
)
from knx_gui.types import (
    DeviceConfig,
    DeviceTemplate,
    listen_obj,
    send_obj,
)

DEVICE_TEMPLATES: dict[str, DeviceTemplate] = {
    "switch_actuator": DeviceTemplate(
        name="Switch Actuator",
        com_objects=[
            listen_obj("Switch", DPT_SWITCH),
            send_obj("Status", DPT_SWITCH),
        ],
        config=DeviceConfig("ABB", "SA/S 4.16.2.2", "2CDG110252R0011", "1.2.3"),
    ),
    "dimmer_actuator": DeviceTemplate(
        name="Dimmer Actuator",
        com_objects=[
            listen_obj("Switch", DPT_SWITCH),
            send_obj("Status", DPT_SWITCH),
            listen_obj("Dimming", DPT_DIMMING),
            listen_obj("Brightness", DPT_PERCENT),
            send_obj("Value", DPT_PERCENT),
        ],
        config=DeviceConfig("ABB", "DA/S 4.230.2.1", "2CDG110198R0011", "2.1.0"),
    ),
    "temperature_sensor": DeviceTemplate(
        name="Temperature Sensor",
        com_objects=[
            send_obj("Temperature", DPT_TEMPERATURE),
        ],
        config=DeviceConfig("Siemens", "QMX3.P37", "5WG1258-3AB13", "3.0.1"),
    ),
    "push_button": DeviceTemplate(
        name="Push Button",
        com_objects=[
            send_obj("Press", DPT_SWITCH),
            send_obj("Long Press", DPT_SWITCH),
            send_obj("Scene", DPT_SCENE),
        ],
        config=DeviceConfig("Gira", "Tastsensor 4 Plus", "2104..", "1.0.5"),
    ),
    "blinds_actuator": DeviceTemplate(
        name="Blinds Actuator",
        com_objects=[
            listen_obj("Move", DPT_UP_DOWN),
            send_obj("Position", DPT_PERCENT),
            listen_obj("Stop", DPT_STOP),
            listen_obj("Slat", DPT_PERCENT),
            send_obj("Slat Pos", DPT_PERCENT),
        ],
        config=DeviceConfig("MDT", "JAL-0410M.02", "JAL-0410M", "2.5.1"),
    ),
    "shutter_button": DeviceTemplate(
        name="Shutter Button",
        com_objects=[
            send_obj("Up/Down", DPT_UP_DOWN),
            send_obj("Stop", DPT_STOP),
        ],
        config=DeviceConfig("Gira", "Jalousie Button", "2104J", "1.0.2"),
    ),
    "rgb_controller": DeviceTemplate(
        name="RGB Controller",
        com_objects=[
            listen_obj("Switch", DPT_SWITCH),
            send_obj("Status", DPT_SWITCH),
            listen_obj("Color", DPT_RGB),
            send_obj("Color Status", DPT_RGB),
            listen_obj("Brightness", DPT_PERCENT),
        ],
        config=DeviceConfig("MDT", "AKD-0424R2.02", "R2.02", "1.1.0"),
    ),
    "logic_gate": DeviceTemplate(
        name="Logic Gate",
        com_objects=[
            listen_obj(
                "Input A",
                DPT_SWITCH,
                supported=[DPT_SWITCH, DPT_BOOL, DPT_UP_DOWN, DPT_OPEN_CLOSE],
            ),
            listen_obj(
                "Input B",
                DPT_SWITCH,
                supported=[DPT_SWITCH, DPT_BOOL, DPT_UP_DOWN, DPT_OPEN_CLOSE],
            ),
            send_obj(
                "Output",
                DPT_SWITCH,
                supported=[DPT_SWITCH, DPT_BOOL, DPT_UP_DOWN, DPT_OPEN_CLOSE],
            ),
        ],
        config=DeviceConfig("MDT", "Logic AKK-04UP.03", "AKK-04UP", "1.0.0"),
    ),
    "thermostat": DeviceTemplate(
        name="Thermostat",
        com_objects=[
            listen_obj("Setpoint", DPT_TEMPERATURE, read_on_init=True),
            send_obj("Actual Temp", DPT_TEMPERATURE),
            send_obj("Heating", DPT_SWITCH, read=False),
            send_obj("Valve", DPT_PERCENT),
        ],
        config=DeviceConfig("Theben", "RAMSES 718 P", "7189210", "2.3.1"),
    ),
}
