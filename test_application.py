from src.mptt_reader.reader import MPTTReader
from src.mptt_reader.logger import MPTTLogger
from src.mptt_reader.constants import Variable
from time import sleep



if __name__ == "__main__":
    reader = MPTTReader("COM3")
    # logger = MPTTLogger(reader, [Variable.BATTERY_VOLTAGE, Variable.POWER_IN])
    while True:
        print("-------------------------")
        print(reader.battery.voltage)
        print(reader.battery.current)
        print(reader.array.voltage)
        print(reader.array.current)
        print(reader.battery.maximum_voltage)
        print(reader.battery.minimum_voltage)
        print(reader.battery.remaining_battery)
        print(reader.array.voltage_target)
        print(reader.utils.dipswitch_bitfield)
        print(reader.utils.alarm_bitfield)
        print(reader.utils.fault_bitfield)
        print(reader.watchdog.alarms)
        print(reader.watchdog.faults)
        sleep(1)
    # reader.overrides.battery_voltage_regulation.set_value(3) # NOTICE: You haven't locked yet! You may have set the value, but not gotten a lock on the override.
    # reader.overrides.battery_voltage_regulation.lock() # Now, it will start updating with your given value and you can change it.
    # reader.overrides.battery_voltage_regulation.set_value(5) # If you set too high or a too low value, you could cause a fault!
    # reader.overrides.battery_voltage_regulation.unlock() # Now it will return control to the slave, make sure to unlock or you will just keep the same value forever.