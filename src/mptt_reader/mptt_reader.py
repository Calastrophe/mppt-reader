import continuous_threading
from pymodbus.client import ModbusSerialClient
from src.mptt_reader.mptt_constants import Register, SCALING_CONSTANT
from time import sleep

# Configuration for continous threading...
continuous_threading.set_allow_shutdown(True)
continuous_threading.set_shutdown_timeout(0)



# Establishes a serial connection on the provided port, the default is COM3. The update interval is when the register state is updated.
class MPTTReader:
    def __init__(self, port: str="COM3", update_interval: float=1):
        self.state: list[int] = []
        self.client: ModbusSerialClient = ModbusSerialClient(port=port, baudrate=9600, method='rtu', timeout=1)
        self.client.connect()
        self.updater = MPTTUpdater(self, update_interval)
        self.overrides = MPTTOverrides(self)
        self.battery = MPTTBattery(self)
        self.array = MPTTArray(self)
        self.utils = MPTTUtilities(self)

    @property
    def voltage_scaling(self):
        return self.state[Register.VoltScalingHi] + (self.state[Register.VoltScalingLo] / 2**16)
    
    @property
    def current_scaling(self):
        return self.state[Register.CurrScalingHi] + (self.state[Register.CurrScalingLo] / 2**16)
    
    def turn_on(self):
        __update_thread = continuous_threading.Thread(target=self.updater.update).start()

    def __del__(self):
        self.client.close()


class MPTTUpdater:
    def __init__(self, reader: MPTTReader, update_interval: float):
        self.reader = reader
        self.update_interval = update_interval
        self.reader.state = self.reader.client.read_holding_registers(0, 94, 1).registers

    def update(self):
        while True:
            assert(self.update_interval < 55)
            self.reader.state = self.reader.client.read_holding_registers(0, 94, 1).registers
            ## Update the values of the manually controlled variables, if we have them locked.
            self.reader.overrides.battery_current_regulation.update()
            self.reader.overrides.battery_voltage_regulation.update()
            self.reader.overrides.array_voltage_target.update()
            sleep(self.update_interval)


# A class to clearly hold the overrides.
class MPTTOverrides:
    def __init__(self, reader: MPTTReader):
        self.battery_voltage_regulation = MPTTOverride(reader, Register.BatteryVoltageRegulation, lambda x: (x / reader.voltage_scaling) / SCALING_CONSTANT)
        self.battery_current_regulation = MPTTOverride(reader, Register.BatteryCurrentRegulation, lambda x: (x / 80) / SCALING_CONSTANT)
        self.array_voltage_target = MPTTOverride(reader, Register.ArrayVoltageTarget, lambda x: (x / reader.voltage_scaling) / SCALING_CONSTANT)


# A class to help abstract the control of a manually controllable variable.
# Similar to a mutex, you have to release control and take control.
# Make sure to use unlock() when you don't want to control the variable anymore! Otherwise, it'll be stuck at one number...
# The third parameter is a lambda function which calculates the correct value. Relative referencing to objects is annoying, but avoids inheritance.
class MPTTOverride:
    def __init__(self, reader: MPTTReader, register: Register, formula):
        self.reader = reader
        self.__register = register+1 # Need to add one for the offset based off array-access.
        self.__locked = False
        self.__formula = formula
        self.__held_value = self.__formula(-1)
        self.__result_value = self.__formula(-1)

    def lock(self):
        self.__locked = True
    
    def set_value(self, new_value: float):
        self.__held_value = self.__formula(new_value)

    def update(self):
        if self.__locked:
            self.reader.client.write_register(self.__register, self.__held_value, 1)

    def unlock(self):
        self.__locked = False
        self.reader.client.write_register(self.__register, self.__result_value, 1)



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
    reader.turn_on()
    while True:
        print(reader.battery.voltage)
        print(reader.battery.current)
        print(reader.array.voltage)
        print(reader.array.current)
        print(reader.battery.maximum_voltage)
        print(reader.battery.minimum_voltage)
        print(reader.battery.remaining_battery)
        sleep(1)
    # reader.overrides.battery_voltage_regulation.set_value(3) # NOTICE: You haven't locked yet! You may have set the value, but not gotten a lock on the override.
    # reader.overrides.battery_voltage_regulation.lock() # Now, it will start updating with your given value and you can change it.
    # reader.overrides.battery_voltage_regulation.set_value(5) # If you set too high or a too low value, you could cause a fault!
    # reader.overrides.battery_voltage_regulation.unlock() # Now it will return control to the slave, make sure to unlock or you will just keep the same value forever.

