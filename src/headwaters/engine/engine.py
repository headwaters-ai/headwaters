import random
import time

"""I think this will become an object that holds its state of things
like frequency, and event scheme, which can be accessed and set

This was overly complex with multi threads per worker, but each engine 
will be simple to start, espcielly in this explore stage, so simplfiy and 
take out second layer of threading.



"""


class Engine:

    """this feels like a template object for an engine....

    the generate method could call a domain thing, data etc, and the domain is passed
    to the enginer object, but everythign else is standard. this engine object could be
    instantiated in the cli or the server and then have it's methods called directly,
    avoiding queues. they could also all just run on the main thread until it becomes necessary
    to use threads, seems like unesserayc complexity for now. or i'll smh when i refactor and reslie why...
    """

    def __init__(self, domain, sio_app) -> None:
        self.domain = domain
        self.sio = sio_app
        self.frequency = 1.0
        self.run = True

        # self.generate()  # to auto start, is this legit to call here?

    def generate(self):
        """generates new data and places onto emit_q"""

        while self.run == True:
            
            event = self.domain.get_event()
            print(f"engine called domain {event}")
            self.sio.emit("stream", data=event)
            print("emitted event")

            # TODO there will NEED to be a max freq for performance and CPU etc

            time.sleep(self.frequency)

    def set_frequency(self, new_freq):
        """Setter for frequency"""
        self.frequency = new_freq

    def stop(self):
        """set self.run to False and stop engine"""
        self.run = False

    def start(self):
        """set self.run to True and start engine"""
        self.run = True
        self.sio.start_background_task(self.generate)

        return "started"
