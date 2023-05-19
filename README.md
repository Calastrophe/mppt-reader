# MPPT-Reader

A quick and easy framework for data-logging and interfacing with a Tristar-MPPT-45 Solar Controller over a serial connection.

You can download the library through pip with `pip install mppt_reader`

To directly interface with the solar controller, use the `MPPTReader` class. It provides access to *most* variables, even if not it is easy to add.
Additionally, if you want to log certain variables, use the `MPPTLogger` class and pass it a MPPTReader instance.

### Overrides
This library allows for you to change regulations in the solar controller, which relate to voltage targets. To do so, you need to set a value.

Initially, the override is unlocked, which means that the value you set isn't being written. To have your value written, you need to call `.lock()` on the override.

You can change the value without unlocking, but its important to remember that you are in control of the value until you call `.unlock()`. After unlocking, it returns control back to the solar controller.

##### Addendum for Overrides
If you were to lock an override and your software crashes, the values will still be written to the solar controller, but after 60 seconds - a fault is thrown and values are taken over by the solar controller again.

For this reason, you can't set `update_interval` of MPPTReader greater than 55.

```py
from mppt_reader.reader import MPPTReader
from mppt_reader.logger import MPPTLogger
from mppt_reader.constants import Variable

reader = MPPTReader("COM3")
# You must provide variables, but file_name will default to the current date and time. Update interval is normally 1 second.
logger = MPPTLogger(reader, variables=[Variable.BATTERY_VOLTAGE, Variable.ARRAY_VOLTAGE], file_name="output", update_interval=2)
# Now it will be logging all variables every second to output.csv and you can still mess with the MPTTReader
reader.overrides.battery_voltage_regulation.set_value(11)
# The value is set, but is not currently controlling the actual voltage regulation.
reader.overrides.battery_voltage_regulation.lock() 
# Now, it will start updating with your given value and you can change it.
reader.overrides.battery_voltage_regulation.set_value(10) 
# If you set too high or a too low value, you could cause a fault!
reader.overrides.battery_voltage_regulation.unlock()
# Now it will return control to the slave, make sure to unlock or you will just keep the same value forever.
```
