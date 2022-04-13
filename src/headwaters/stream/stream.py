import logging
from multiprocessing.sharedctypes import Value
import time
from datetime import datetime


class Stream:

    """blueprint for an Stream, which is passed a source class instance to call for data"""

    def __init__(self, source, sio_app) -> None:

        if not isinstance(source, int):
            pass
        self.source = source
        self.sio = sio_app

        self.name = self.source.name

        self.freq = 1_000
        self.freq_min = 100
        self.running = True

        self.limit_mode = False
        self.limit = 10
        self.limit_counter = 0

        self.burst_mode = False
        self.burst_vol = 100
        self.burst_vol_min = 1
        self.burst_counter = 0
        self.burst_freq = 100
        self.burst_freq_min = 50

    def start(self) -> str:
        """set self.running to True and start stream if it is stopped

        guards against multiple starts
        """
        if not self.running:
            self.running = True
            self.limit_counter = 0
            self.sio.start_background_task(self.flow)
        else:
            raise ValueError(f"stream {self.name} already running")

    def stop(self):
        """set self.running to False and stop stream if it is running
        
        includes stopping the burst mode
        """

        if self.running:
            self.running = False
            # stop burst mode too, and need to rest counter too
            self.burst_mode = False
            self.burst_counter = 0
        else:
            raise ValueError(f"stream {self.name} already stopped")

    @property
    def stream_status(self) -> dict:
        """return key properties of the stream instance"""

        status = {
            "stream_name": self.name,
            "running": self.running,
            "stream_freq": self.freq,
            "burst_mode_active": self.burst_mode,
            "burst_freq": self.burst_freq,
            "burst_vol": self.burst_vol
        }

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
                if self.burst_counter <= self.burst_vol:
                    self.collect_emit()
                    self.burst_counter += 1
                else:
                    self.burst_mode = False
                    self.burst_counter = 0

                time.sleep(self.burst_freq / 1_000)

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

        if isinstance(new_freq, int) and new_freq >= self.freq_min:
            self.freq = new_freq
        else:
            raise ValueError(
                f"new stream frequency (new_freq) must be int gte {self.freq_min}ms, supplied value was {new_freq}"
            )

    def start_burst(self):
        """start a burst

        guard against double burst checking mode is false before
        """
        if not self.burst_mode:
            self.burst_mode = True
        else:
            raise ValueError(f"burst mode is already active")

    def set_burst_freq(self, burst_freq):
        """setter to adjust burst freqency"""

        if not isinstance(burst_freq, int):
            raise TypeError(f'TypeError: burst frequency (burst_freq) must be an integer; supplied type was {type(burst_freq)}')
        
        if burst_freq >= self.burst_freq_min:
            self.burst_freq = burst_freq
        else:
            raise ValueError(
                f"ValueError: burst freq (burst_freq) must be gte {self.burst_freq_min}; supplied value was {burst_freq}"
            )

    def set_burst_vol(self, burst_vol):
        """setter to adjust burst volume"""
        
        if not isinstance(burst_vol, int):
            raise TypeError(f'TypeError: burst volume (burst_vol) must be an integer; supplied type was {type(burst_vol)}')
        
        if burst_vol >= self.burst_vol_min:
            self.burst_vol = burst_vol
        else:
            raise ValueError(
                f"ValueError: burst volume (burst_vol) must be gte {self.burst_vol_min}; supplied value was {burst_vol}"
            )

    def set_error_mode_on(self):
        """setter to set error mode for source to on"""
        self.source.error_mode = True

    def set_error_mode_off(self):
        """setter to set error mode for source to off"""
        self.source.error_mode = False
