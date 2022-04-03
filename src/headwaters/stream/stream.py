import logging
import time

class Stream:

    """blueprint for an Stream, which is passed a source class instance to call for data
    
    """

    def __init__(self, source, sio_app) -> None:

        if not isinstance(source, int):
            pass
        self.source = source
        self.sio = sio_app

        self.name = self.source.name

        self.freq = 1_000
        self.running = True

        self.limit_mode = False
        self.limit = 10
        self.limit_counter = 0

        self.burst_mode = False
        self.burst_limit = 30
        self.burst_counter = 0
        self.burst_frequency = 0.2

    def start(self) -> str:
        """set self.running to True and start stream if it is stopped

        guards against multiple starts
        """
        if not self.running:
            self.running = True
            self.limit_counter = 0
            self.sio.start_background_task(self.flow)
            logging.info(f"stream {self.name} started")
            return f"stream {self.name} started"
        else:
            return f"stream {self.name} already running"

    def stop(self):
        """set self.running to False and stop stream if it is running"""

        if self.running:
            self.running = False
            return f"stream {self.name} stopped"
        else:
            return f"stream {self.name} already stopped"

    @property
    def stream_status(self) -> dict:
        """return key properties of the stream instance"""

        status = {"stream_name": self.name, "running": self.running}

        return status

    def flow(self):
        """schedules and runs the loop that calls the collect_emit method"""

        while self.running == True:
            if self.limit_mode:
                if self.limit_counter < self.limit:

                    self.collect_emit()
                    self.limit_counter += 1
                else:
                    self.stop()

                time.sleep(self.freq / 1_000)

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
                time.sleep(self.freq / 1_000)

    def collect_emit(self):
        """collects new event data from the passed source instance and emits event
        
        the event name is set to the name of the source and stream ie 'fruits'
        """

        event = self.source.new_event()
        self.sio.emit(self.name, data=event)

    def set_freq(self, new_freq):
        """Setter for frequency"""
        self.freq = new_freq

    def set_burst(self):
        """setter to start a burst"""
        self.burst_mode = True

    def set_error_mode_on(self):
        """setter to set error mode for source to on"""
        self.source.error_mode = True

    def set_error_mode_off(self):
        """setter to set error mode for source to off"""
        self.source.error_mode = False

    def burst(self):
        """trigger burst mode"""
        pass
