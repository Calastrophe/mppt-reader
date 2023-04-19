import continuous_threading
from pymodbus.client import ModbusSerialClient
from .constants import Register, SCALING_CONSTANT, FAULTS, ALARMS, CHARGE_STATE, LED_STATE
from time import sleep

# Configuration for continous threading...
continuous_threading.set_allow_shutdown(True)
continuous_threading.set_shutdown_timeout(0)



# Establishes a serial connection on the provided port, the default is COM3. The update interval is when the register state is updated.
class MPPTReader:
    def __init__(self, port: str="COM3", update_interval: float=1, watchdog_interval: float=5):
        self.state: list[int] = []
        self.client: ModbusSerialClient = ModbusSerialClient(port=port, baudrate=9600, method='rtu', timeout=1)
        self.client.connect()
        self.updater = MPPTUpdater(self, update_interval)
        self.overrides = MPPTOverrides(self)
        self.battery = MPPTBattery(self)
        self.array = MPPTArray(self)
        self.utils = MPPTUtilities(self)
        self.watchdog = MPPTWatchdog(self, watchdog_interval)
        _ = continuous_threading.Thread(target=self.updater.update).start()

    @property
    def voltage_scaling(self):
        return self.state[Register.VoltScalingHi] + (self.state[Register.VoltScalingLo] / 2**16)
    
    @property
    def current_scaling(self):
        return self.state[Register.CurrScalingHi] + (self.state[Register.CurrScalingLo] / 2**16)

    def __del__(self):
        self.client.close()


class MPPTUpdater:
    def __init__(self, reader: MPPTReader, update_interval: float):
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

class MPPTWatchdog:
    def __init__(self, reader: MPPTReader, watchdog_interval: float):
        self.reader = reader
        self.watchdog_interval = watchdog_interval
        self.alarms, self.faults = ([], [])
        _ = continuous_threading.Thread(target=self._watchdog_thread).start()

    def _watchdog_thread(self):
        while True:
            self.faults: list[str] = [FAULTS[i] for i, bit in enumerate(self.reader.utils.fault_bitfield) if bit == '1']
            self.alarms: list[str] = [ALARMS[i] for i, bit in enumerate(self.reader.utils.alarm_bitfield) if bit == '1']
            sleep(self.watchdog_interval)


# A class to clearly hold the overrides.
class MPPTOverrides:
    def __init__(self, reader: MPPTReader):
        self.battery_voltage_regulation = MPPTOverride(reader, Register.BatteryVoltageRegulation, lambda x: (x / reader.voltage_scaling) / SCALING_CONSTANT)
        self.battery_current_regulation = MPPTOverride(reader, Register.BatteryCurrentRegulation, lambda x: (x / 80) / SCALING_CONSTANT)
        self.array_voltage_target = MPPTOverride(reader, Register.ArrayVoltageTarget, lambda x: (x / reader.voltage_scaling) / SCALING_CONSTANT)


# A class to help abstract the control of a manually controllable variable.
# Similar to a mutex, you have to release control and take control.
# Make sure to use unlock() when you don't want to control the variable anymore! Otherwise, it'll be stuck at one number...
# The third parameter is a lambda function which calculates the correct value. Relative referencing to objects is annoying, but avoids inheritance.
class MPPTOverride:
    def __init__(self, reader: MPPTReader, register: Register, formula):
        self.reader = reader
        self.__register = register+1 # Need to add one for the offset based off array-access.
        self.__locked = False
        self.__formula = formula
        self.__value = self.__formula(-1)
        self.__reset_value = self.__formula(-1)

    def lock(self):
        self.__locked = True
    
    def set_value(self, new_value: float):
        self.__value = self.__formula(new_value)

    def update(self):
        if self.__locked:
            self.reader.client.write_register(self.__register, self.__value, 1)

    def unlock(self):
        self.__locked = False
        self.reader.client.write_register(self.__register, self.__reset_value, 1)



class MPPTBattery:
    def __init__(self, reader: MPPTReader):
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
    
    # Fahrenheit
    @property
    def temperature_f(self):
        return (self.reader.state[Register.BatteryTemp] * 9/5) + 32
    
    # Celsius
    @property
    def temperature_c(self):
        return self.reader.state[Register.BatteryTemp]
    

class MPPTArray:
    def __init__(self, reader: MPPTReader):
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
    

class MPPTUtilities:
    def __init__(self, reader: MPPTReader):
        self.reader = reader
    

    @property
    def heatsink_temp(self):
        return self.reader.state[Register.HeatSinkTemp]
    
    @property
    def rts_temp(self):
        return self.reader.state[Register.RTSTemp]

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
    
    @property
    def led_state(self) -> str:
        return LED_STATE[self.reader.state[Register.LEDState]]
    
    @property
    def charge_state(self) -> str:
        return CHARGE_STATE[self.reader.state[Register.ChargeState]]
    

    ## These bitfields are read in reverse to easily match an on-bit to its string counterpart from constants.
    @property
    def alarm_bitfield(self):
        return (_binarize(self.reader.state[Register.AlarmHI]) + _binarize(self.reader.state[Register.AlarmLO]))[::-1]
    
    @property
    def fault_bitfield(self):
        return _binarize(self.reader.state[Register.FaultBits])[::-1]
    
    @property
    def dipswitch_bitfield(self):
        return _binarize(self.reader.state[Register.DipswitchBits])[::-1]


# Utility function to make bitfields
def _binarize(num: int) -> str:
    return ((bin(num)[2:]).zfill(16)) # 16 is the size of a word on this "computer"