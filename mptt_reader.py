from pymodbus.client import ModbusSerialClient
from mptt_constants import Register, SCALING_CONSTANT
from time import sleep
from threading import Thread




# Establishes a serial connection on the provided port, the default is COM3. The update interval is when the register state is updated.
class MPTTReader:
    def __init__(self, port: str="COM3", update_interval: float=0.5):
        self.state: list[int] = []
        self.client: ModbusSerialClient = ModbusSerialClient(port=port, baudrate=9600, method='rtu', timeout=1)
        self.client.connect()
        self.updater = MPTTUpdater(self, update_interval)
        self.battery = MPTTBattery(self)
        self.array = MPTTArray(self)
        self.utils = MPTTUtilities(self)

    @property
    def voltage_scaling(self):
        return self.state[Register.VoltScalingHi] + (self.state[Register.VoltScalingLo] / 2**16)
    
    @property
    def current_scaling(self):
        return self.state[Register.CurrScalingHi] + (self.state[Register.CurrScalingLo] / 2**16)
    
    ## OVERRIDES - MOVE TO BATTERY & ARRAY CLASSES LATER
    def set_batt_volt_reg(self, new_value: float):
        passed_value = (new_value / self.voltage_scaling) / SCALING_CONSTANT
        self.updater.battery_voltage_regulation = passed_value

    def set_batt_curr_reg(self, new_value: float):
        passed_value = (new_value / 80) / SCALING_CONSTANT
        self.updater.battery_current_regulation = passed_value

    def set_arr_volt_target(self, new_value: float):
        passed_value = (new_value / self.voltage_scaling) / SCALING_CONSTANT
        self.updater.array_voltage_target = passed_value

    ## Percentage will overwrite the target, so just choose one.
    def set_arr_volt_target_percent(self, new_value: float):
        passed_value = (new_value / 100) / 2**(-16)
        self.updater.array_voltage_target_percentage = passed_value


    def __del__(self):
        self.client.close()


class MPTTUpdater:
    def __init__(self, reader: MPTTReader, update_interval: float):
        self.reader = reader
        self.update_interval = update_interval
        self.grab_overrides()
        self.__update_thread = Thread(self.__update)
        self.__update_thread.start()

    def grab_overrides(self):
        self.reader.state = self.reader.client.read_holding_registers(0, 92, 1)
        self.battery_voltage_regulation = self.reader.state[Register.BatteryVoltageRegulation]
        self.battery_current_regulation = self.reader.state[Register.BatteryCurrentRegulation]
        self.array_voltage_target = self.reader.state[Register.ArrayVoltageTarget]
        self.array_voltage_target_percentage = self.reader.state[Register.ArrayVoltageTargetPercentage]

    def __update(self):
        while True:
            assert(self.update_interval < 55)
            self.state = self.client.read_holding_registers(0, 94, 1).registers
            # See if ths multiple-write register works or not.
            self.reader.client.write_registers(Register.BatteryCurrentRegulation+1, [self.battery_current_regulation, self.battery_voltage_regulation, self.array_voltage_target, self.array_voltage_target_percentage], 1)
            # self.reader.client.write_register(Register.BatteryCurrentRegulation+1, self.battery_current_regulation, 1)
            # self.reader.client.write_register(Register.BatteryVoltageRegulation+1, self.battery_voltage_regulation, 1)
            # self.reader.client.write_register(Register.ArrayVoltageTarget+1, self.array_voltage_target, 1)
            # self.reader.client.write_register(Register.ArrayVoltageTargetPercentage+1, self.array_voltage_target_percentage, 1)
            sleep(self.update_interval)

    def __del__(self):
        self.__update_thread.join()


class MPTTBattery:
    def __init__(self, reader: MPTTReader):
        self.reader = reader

    @property
    def voltage(self):
        return self.reader.voltage_scaling * self.reader.state[Register.BatteryVolt] * SCALING_CONSTANT
    
    @property
    def terminal_voltage(self):
        return self.reader.voltage_scaling * self.reader.state[Register.BatteryTermVolt] * SCALING_CONSTANT
    
    @property
    def minimum_voltage(self):
        return self.reader.state[Register.MinBatteryVolt] * self.reader.voltage_scaling * SCALING_CONSTANT
    
    @property
    def maximum_voltage(self):
        return self.reader.state[Register.MaxBatteryVolt] * self.reader.voltage_scaling * SCALING_CONSTANT
    
    @property
    def voltage_regulation(self):
        return self.reader.state[Register.BatteryVoltageRegulation] * self.reader.voltage_scaling * SCALING_CONSTANT
    
    @property
    def current(self):
        return self.reader.current_scaling * self.reader.state[Register.BatteryCurrent] * SCALING_CONSTANT
    
    @property
    def current_regulation(self):
        return self.reader.state[Register.BatteryCurrentRegulation] * 80 * SCALING_CONSTANT
    
    @property
    def remaining_battery(self):
        return (self.terminal_voltage - self.minimum_voltage) / (self.maximum_voltage - self.minimum_voltage)
    

class MPTTArray:
    def __init__(self, reader: MPTTReader):
        self.reader = reader

    @property
    def voltage(self):
        return self.reader.voltage_scaling * self.reader.state[Register.ArrayVolt] * SCALING_CONSTANT
    
    @property
    def current(self):
        return self.reader.current_scaling * self.reader.state[Register.ArrayCurrent] * SCALING_CONSTANT
    
    @property
    def voltage_target(self):
        return self.reader.state[Register.ArrayVoltageTarget] * self.reader.voltage_scaling * SCALING_CONSTANT
    
    @property
    def voltage_target_percent(self):
        return self.reader.state[Register.ArrayVoltageTargetPercentage] * 100 * 2**(-16)
    

class MPTTUtilities:
    def __init__(self, reader: MPTTReader):
        self.reader = reader
    
    ## TEMPERATURES

    @property
    def heatsink_temp(self):
        return self.reader.state[Register.HeatSinkTemp]
    
    @property
    def rts_temp(self):
        return self.reader.state[Register.RTSTemp]
    
    ## POWER-RELATED

    @property
    def voltsupply12(self):
        return self.reader.state[Register.VoltSupply12]
    
    @property
    def voltsupply3(self):
        return self.reader.state[Register.VoltSupply3]
    
    @property
    def power_in(self):
        return self.reader.voltage_scaling * self.reader.current_scaling * self.reader.state[Register.InputPower] * 2**(-17)
    
    @property
    def power_out(self):
        return self.reader.voltage_scaling * self.reader.current_scaling * self.reader.state[Register.OutputPower] * 2**(-17)

    






if __name__ == "__main__":
    reader = MPTTReader("COM3")
    print(reader.battery.voltage)
    print(reader.battery.current)
    print(reader.array.voltage)
    print(reader.array.current)
    print(reader.battery.maximum_voltage)
    print(reader.battery.minimum_voltage)
    print(reader.battery.remaining_battery)