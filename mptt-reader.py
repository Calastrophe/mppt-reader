from pymodbus.client import ModbusSerialClient
from time import sleep
from threading import Thread
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


# Establishes a serial connection on the provided port, the default is COM3. Change if needed.
class MPTTReader:
    def __init__(self, port: str="COM3", update_interval: float=0.5):
        self.client = ModbusSerialClient(port=port, baudrate=9600, method='rtu', timeout=1)
        self.client.connect()
        self.state: list[int] = []
        self.scaling_constant = 2**(-15)
        self.update_interval = update_interval
        self.__update_thread = Thread(target=self.__update)
        self.__update_thread.start()


    def __update(self):
        while True:
            self.state = self.client.read_holding_registers(0, 88, 1).registers
            sleep(self.update_interval)
            

    @property
    def voltage_scaling(self):
        return self.state[Register.VoltScalingHi] + (self.state[Register.VoltScalingLo] / 2**16)
    
    @property
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
    def heatsink_temp(self):
        return self.state[Register.HeatSinkTemp]
    
    @property
    def rts_temp(self):
        return self.state[Register.RTSTemp]
    
    @property
    def voltsupply12(self):
        return self.state[Register.VoltSupply12]
    
    @property
    def voltsupply3(self):
        return self.state[Register.VoltSupply3]
    
    @property
    def power_in(self):
        return self.voltage_scaling * self.current_scaling * self.state[Register.InputPower] * 2**(-17)
    
    @property
    def power_out(self):
        return self.voltage_scaling * self.current_scaling * self.state[Register.OutputPower] * 2**(-17)

    def __del__(self):
        self.__update_thread.join()
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
