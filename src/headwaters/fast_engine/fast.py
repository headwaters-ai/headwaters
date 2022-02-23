import threading
from queue import Queue
import random
import time

"""I think this will become an object that holds its state of things
like frequency, and event scheme, which can be accessed and set

This was overly complex with multi threads per worker, but each engine 
will be simple to start, espcielly in this explore stage, so simplfiy and 
take out second layer of threading.



"""

class Fast:

    """ this feels like a template object for an engine....
    
    the generate method could call a domain thing, data etc, and the domain is passed
    to the enginer object, but everythign else is standard. this engine object could be
    instantiated in the cli or the server and then have it's methods called directly,
    avoiding queues. they could also all just run on the main thread until it becomes necessary 
    to use threads, seems like unesserayc complexity for now. or i'll smh when i refactor and reslie why...
    """

    def __init__(self, emit_q, cmd_q) -> None:
        self.emit_q = emit_q
        self.cmd_q = cmd_q
        self.frequency = 1.0
        self.run = True

        self.generate() # to auto start, is this legit to call here?

    def generate(self):
        """ generates new data and places onto emit_q
        
        """
        
        while self.run == True:
            item = {
                "topic": "speedyfastness",
                "payload": random.random()
            }
            self.emit_q.put(item)

            # poll the cmd_q here. if a value, set freq to that, else pass

            if not self.cmd_q.empty():
                self.set_frequency(self.cmd_q.get())

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

# def mgr(emit_q):

#     """ currently being called as the target of the cli thread creation
#     """

#     print(f"this is {__name__} probably headwaters.fast_engine.fast")

#     # create an internal engine tuning_q here

#     threads = []

#     num_thr = 1

#     for _ in range(num_thr):
#         worker = Worker(emit_q) # passes the emit_q in object init, so not needed as args to thread
#         threads.append(threading.Thread(target=worker.generate)) # pass tuning_q

#     for thread in threads:
#         thread.start()

#     for thread in threads:
#         thread.join()