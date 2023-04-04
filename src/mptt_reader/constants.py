from enum import IntEnum

SCALING_CONSTANT = 2**(-15)

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