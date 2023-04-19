import continuous_threading
from .reader import MPPTReader
from .constants import Variable
from datetime import datetime
from time import sleep


class MPPTLogger:
    def __init__(self, mptt_reader: MPPTReader, variables: list[Variable], file_name=None, update_interval=1):
        self.reader = mptt_reader
        self._callbacks: list[Variable] = variables
        self.update_interval = update_interval
        self.fn = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}" if file_name is None else file_name
        __logging_thread = continuous_threading.Thread(target=self.__logging_function).start()


    def __logging_function(self):
        with open(f"{self.fn}.csv", "w") as fd:
            fd.write("TIME,")
            fd.write(",".join(var.name for var in self._callbacks) + "\n")
            while True:
                values = []
                fd.write(f"{datetime.now().strftime('%H:%M:%S')},")
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
