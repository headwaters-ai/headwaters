import logging
import time

logging.basicConfig(level=logging.DEBUG)
"""I think this will become an object that holds its state of things
like frequency, and event scheme, which can be accessed and set

This was overly complex with multi threads per worker, but each engine 
will be simple to start, espcielly in this explore stage, so simplfiy and 
take out second layer of threading.

"""


class Engine:

    """blueprint for an engine, which is passed a domain class instance to call for data"""

    def __init__(self, domain, sio_app) -> None:
        self.domain = domain
        self.sio = sio_app

        self.frequency = 1.0
        self.run = True

        self.limit_mode = False
        self.limit = 10
        self.limit_counter = 0

        self.burst_mode = False
        self.burst_limit = 30
        self.burst_counter = 0
        self.burst_frequency = 0.2

    def collect_emit(self):
        """collects new event data from the passed domain instance and emits event"""

        event = self.domain.new_event()
        # logging.info(f"engine called domain {event}")
        self.sio.emit("stream", data=event)

    def generate(self):
        """generates new data and emits"""

        while self.run == True:
            if self.limit_mode:
                if self.limit_counter < self.limit:

                    self.collect_emit()
                    self.limit_counter += 1
                else:
                    self.stop()

                time.sleep(self.frequency)

            if self.burst_mode:
                if self.burst_counter < self.burst_limit:
                    self.collect_emit()
                    self.burst_counter += 1
                else:
                    self.burst_mode = False
                    self.burst_counter = 0
                time.sleep(self.burst_frequency)

            else:
                self.collect_emit()
                time.sleep(self.frequency)

    def set_frequency(self, new_freq):
        """Setter for frequency"""
        self.frequency = new_freq

    def set_burst(self):
        """setter to start a burst"""
        self.burst_mode = True

    def set_error_mode_on(self):
        """setter to set error mode for domain to on"""
        self.domain.error_mode = True

    def set_error_mode_off(self):
        """setter to set error mode for domain to off"""
        self.domain.error_mode = False

    def stop(self):
        """set self.run to False and stop engine"""
        self.run = False

    def start(self):
        """set self.run to True and start engine"""
        self.run = True
        self.limit_counter = 0
        self.sio.start_background_task(self.generate)

    def burst(self):
        """trigger burst mode"""
