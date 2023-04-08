from enum import IntEnum, StrEnum

SCALING_CONSTANT = 2**(-15)

CHARGE_STATE = ["START", "NIGHT_CHECK", "DISCONNECT", "NIGHT",
                "FAULT", "MPPT", "ABSORPTION", "FLOAT", "EQUALIZE", "SLAVE"]

ALARMS = ["RTS open", "RTS shorted", "RTS disconnected", "Heatsink temp sensor open",
            "Heatsink temp sensor shorted", "High temperature current limit", "Current limit",
            "Current offset", "Battery sense out of range", "Battery sense disconnected",
            "Uncalibrated", "RTS miswire", "High voltage disconnect", "Undefined",
            "system miswire", "MOSFET open", "P12 voltage off", "High input voltage current limit",
            "ADC input max", "Controller was reset", "Alarm 21", "Alarm 22", "Alarm 23", "Alarm 24"]

FAULTS = ["Overcurrent", "FETs shorted", "software bug", "battery HVD", "array HVD",
            "settings switch changed", "custom settings edit", "RTS shorted", "RTS disconnected",
            "EEPROM retry limit", "Reserved", " Slave Control Timeout",
            "Fault 13", "Fault 14", "Fault 15", "Fault 16"]

LED_STATE = ["LED_START", "LED_START2", "LED_BRANCH", "FAST GREEN BLINK", "SLOW GREEN BLINK", "GREEN BLINK, 1HZ",
             "GREEN_LED", "UNDEFINED", "YELLOW_LED", "UNDEFINED", "BLINK_RED_LED", "RED_LED", "R-Y-G ERROR",
             "R/Y-G ERROR", "R/G-Y ERROR", "R-Y ERROR (HTD)", "R-G ERROR (HVD)", "R/Y-G/Y ERROR", "G/Y/R ERROR",
             "G/Y/R x 2"]


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
    POWER_OUT = "utils.power_out",



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
    BatteryTemp = 37,
    BatteryVoltage = 38,
    ChargingCurrent = 39,
    MinBatteryVolt = 40,
    MaxBatteryVolt = 41,
    HourmeterHI = 42,
    HourmeterLO = 43,
    FaultBits = 44,
    AlarmHI = 46,
    AlarmLO = 47,
    DipswitchBits = 48,
    LEDState = 49,
    ChargeState = 50,
    OutputPower = 58,
    InputPower = 59
    BatteryCurrentRegulation = 88,
    BatteryVoltageRegulation = 89,
    ArrayVoltageTarget = 90,
    ArrayVoltageTargetPercentage = 91