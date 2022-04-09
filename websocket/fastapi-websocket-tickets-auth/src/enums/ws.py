from enum import Enum


class WsActionEnum(str, Enum):
    write_value = "write_value"
    write_battery_level = "write_battery_level"
