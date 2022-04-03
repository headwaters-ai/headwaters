import logging
import time

# logging.basicConfig(filename='engine.log', level=logging.DEBUG)


class Engine:

    """blueprint for an engine, which is passed a domain class instance to call for data"""

    def __init__(self, domain, sio_app) -> None:

        if not isinstance(domain, int):
            pass
        self.domain = domain
        self.sio = sio_app

        self.frequency = 1.0
        self.running = True

        self.limit_mode = False
        self.limit = 10
        self.limit_counter = 0

        self.burst_mode = False
        self.burst_limit = 30
        self.burst_counter = 0
        self.burst_frequency = 0.2

    def start(self) -> str:
        """set self.running to True and start engine if it is stopped

        guards against multiple starts
        """
        if not self.running:
            self.running = True
            self.limit_counter = 0
            self.sio.start_background_task(self.generate)
            logging.info(f"engine {self.domain.name} started")
            return f"stream {self.domain.name} started"
        else:
            return f"stream {self.domain.name} already running"

    def stop(self):
        """set self.running to False and stop engine if it is running"""

        if self.running:
            self.running = False
            return f"stream {self.domain.name} stopped"
        else:
            return f"stream {self.domain.name} already stopped"

    @property
    def stream_status(self) -> dict:
        """return key properties of the engine instance"""

        status = {"stream_name": self.domain.name, "running": self.running}

        return status

    def generate(self):
        """schedules and runs the loop for the collect_emit method"""

        while self.running == True:
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

    def collect_emit(self):
        """collects new event data from the passed domain instance and emits event"""

        event = self.domain.new_event()
        self.sio.emit("stream", data=event)

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

    def burst(self):
        """trigger burst mode"""
        pass
