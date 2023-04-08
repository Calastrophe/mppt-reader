# MPPT-Reader

A work in progress way to quickly read from an TRISTAR-MPPT-45. Soon there will be added features to logging the data to unique data formats.

If you use the tool, please leave a star, so others can find it too in their search.

Use `pip install mptt_reader` to download the library.

If you want to just read and modify the MPTT-reader in a pythonic way without logging variables, use `MPTTReader` class.

If you want to log variables, you can just take your `MPTTReader` class and pass it into an `MPTTLogger` instance.

```py
from mptt_reader.reader import MPTTReader
from mptt_reader.logger import MPTTLogger
from mptt_reader.constants import Variable

reader = MPTTReader("COM3")
# You must provide variables, but file_name will default to the current date and time. Update interval is normally 1 second.
logger = MPTTLogger(reader, variables=[Variable.BATTERY_VOLTAGE, Variable.ARRAY_VOLTAGE], file_name="output", update_interval=2)
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
