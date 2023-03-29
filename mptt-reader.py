from pymodbus.client import ModbusSerialClient
from enum import IntEnum

## Taken from : https://www.morningstarcorp.com/wp-content/uploads/technical-doc-tristar-mppt-modbus-specification-en.pdf
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


## Updates the state of the registers before reading and making calculations
def update(method):
    def inner(ref):
        if ref:
            ref.state = ref.client.read_holding_registers(0, 88, 1).registers
            return method(ref)
    return inner


# Establishes a serial connection on the provided port, the default is COM3. Change if needed.
class MPTTReader:
    def __init__(self, port: str= "COM3"):
        self.client = ModbusSerialClient(port=port, baudrate=9600, method='rtu', timeout=1)
        self.client.connect()
        self.state: list[int] = []
        self.scaling_constant = 2**(-15)

    @property
    @update
    def voltage_scaling(self):
        return self.state[Register.VoltScalingHi] + (self.state[Register.VoltScalingLo] / 2**16)
    
    @property
    @update
    def current_scaling(self):
        return self.state[Register.CurrScalingHi] + (self.state[Register.CurrScalingLo] / 2**16)
    
    # In these next two functions, we calculate the scaling first because it will update the register state. If we dont, there will be an out of bounds array access.
    # If we find that the scalings never change, it would be wise to just get rid of the @update decorator on them and leave it only on the other methods.
    # Essentially, having them as constants and each time we go to grab a new variable, it'll update the register state.

    @property
    def battery_voltage(self):
        return self.voltage_scaling * self.state[Register.BatteryVolt] * self.scaling_constant
    
    @property
    def battery_terminal_voltage(self):
        return self.voltage_scaling * self.state[Register.BatteryTermVolt] * self.scaling_constant
    
    @property
    def battery_current(self):
        return self.current_scaling * self.state[Register.BatteryCurrent] * self.scaling_constant
    
    @property
    def array_voltage(self):
        return self.voltage_scaling * self.state[Register.ArrayVolt] * self.scaling_constant
    
    @property
    def array_current(self):
        return self.current_scaling * self.state[Register.ArrayCurrent] * self.scaling_constant
    
    @property
    @update
    def heatsink_temp(self):
        return self.state[Register.HeatSinkTemp]
    
    @property
    @update
    def rts_temp(self):
        return self.state[Register.RTSTemp]
    
    @property
    @update
    def voltsupply12(self):
        return self.state[Register.VoltSupply12]
    
    @property
    @update
    def voltsupply3(self):
        return self.state[Register.VoltSupply3]
    
    @property
    def power_in(self):
        return self.voltage_scaling * self.current_scaling * self.state[Register.InputPower] * 2**(-17)
    
    @property
    def power_out(self):
        return self.voltage_scaling * self.current_scaling * self.state[Register.OutputPower] * 2**(-17)

    def __del__(self):
        self.client.close()






if __name__ == "__main__":
    reader = MPTTReader("COM3")
    print(reader.battery_voltage)
    print(reader.battery_terminal_voltage)
    print(reader.battery_current)
    print(reader.array_voltage)
    print(reader.array_current)
    print(reader.rts_temp)
    print(reader.heatsink_temp)
    print(reader.power_in)
