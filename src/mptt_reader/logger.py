import continuous_threading
from .reader import MPTTReader
from .constants import Variable
from datetime import datetime
from time import sleep


class MPTTLogger:
    def __init__(self, mptt_reader: MPTTReader, initial_variables: list[Variable], output_name=None, update_interval=1):
        self.reader = mptt_reader
        self._callbacks: list[Variable] = initial_variables
        self.update_interval = update_interval
        self.fn = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}" if output_name is None else output_name
        __logging_thread = continuous_threading.Thread(target=self.__logging_function).start()


    def __logging_function(self):
        with open(f"{self.fn}.csv", "w") as fd:
            fd.write(",".join(var.name for var in self._callbacks) + "\n")
            while True:
                values = []
                for var in self._callbacks:
                    if "." in var:
                        owner_object, attr_name = var.split('.')
                        callback_return = getattr(getattr(self.reader, owner_object, None), attr_name, None)
                    else:
                        callback_return = getattr(self.reader, var.value, None)
                    values.append(callback_return)
                fd.write(",".join(str(val) for val in values) + "\n")
                fd.flush()
                sleep(self.update_interval)
