from enum import IntEnum, StrEnum

SCALING_CONSTANT = 2**(-15)

class Variable(StrEnum):
    VOLTAGE_SCALING = "voltage_scaling",
    CURRENT_SCALING = "current_scaling",
    BATTERY_VOLTAGE = "battery.voltage",
    BATTERY_TERMINAL_VOLTAGE = "battery.terminal_voltage",
    BATTERY_MINIMUM_VOLTAGE = "battery.minimum_voltage",
    BATTERY_MAXIMUM_VOLTAGE = "battery.maximum_voltage",
    BATTERY_VOLTAGE_REGULATION = "battery.voltage_regulation",
    BATTERY_CURRENT = "battery.current",
    BATTERY_CURRENT_REGULATION = "battery.current_regulation",
    REMAINING_BATTERY = "battery.remaining_battery",
    ARRAY_VOLTAGE = "array.voltage",
    ARRAY_CURRENT = "array.current",
    ARRAY_VOLTAGE_TARGET = "array.voltage_target"
    ARRAY_VOLTAGE_PERCENT = "array.voltage_target_percent",
    HEATSINK_TEMPERATURE = "utils.heatsink_temp",
    RTS_TEMPERATURE = "utils.rhs_temp",
    VOLT_SUPPLY_12 = "utils.voltsupply12",
    VOLT_SUPPLY_3 = "utils.voltsupply3",
    POWER_IN = "utils.power_in",
    POWER_OUT = "utils.power_out"
    


class Register(IntEnum):
    VoltScalingHi = 0,
    VoltScalingLo = 1,
    CurrScalingHi = 2,
    CurrScalingLo = 3,
    SoftwareVersion = 4,
    BatteryVolt = 24,
    BatteryTermVolt = 25,
    BatterySenseVolt = 26,
    ArrayVolt = 27,
    BatteryCurrent = 28,
    ArrayCurrent = 29,
    VoltSupply12 = 30,
    VoltSupply3 = 31,
    MeterBusVolt = 32,
    RefVoltage = 34
    HeatSinkTemp = 35,
    RTSTemp = 36,
    BatteryRegTemp = 37,
    BatteryVoltage = 38,
    ChargingCurrent = 39,
    MinBatteryVolt = 40,
    MaxBatteryVolt = 41,
    HourmeterHI = 42,
    HourmeterLO = 43,
    OutputPower = 58,
    InputPower = 59
    BatteryCurrentRegulation = 88,
    BatteryVoltageRegulation = 89,
    ArrayVoltageTarget = 90,
    ArrayVoltageTargetPercentage = 91