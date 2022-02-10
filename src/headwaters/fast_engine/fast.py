import threading
from queue import Queue
import random
import time
from dataclasses import dataclass

"""I think this will become an object that holds its state of things
like frequency, and event scheme, which can be accessed and set"""

class Worker:

    def __init__(self, emit_q) -> None:
        self.emit_q = emit_q
        self.frequency = 1.0

 
    def generate(self):
        """ this is an example of the deep generator part of each engine, called by the specfici egnine mgr below
        
        if this was a class, it could be called as target of mgr with worker.generate
        then it could have a setter for frequency worker.set_freq(new_freq)
        
        """
        
        while True:
            item = {
                "topic": "speedyfastness",
                "payload": random.random()
            }
            self.emit_q.put(item)

            # for example, this param of time.sleep is how frequency would be controlled...
            # should this happen at the worker level or up at the mgr?

            # TODO there will NEED to be a max freq for performance and CPU etc

            time.sleep(self.frequency)

    def set_frequency(self, new_freq):
        """Setter for frequency"""
        self.frequency = new_freq

def mgr(emit_q):

    """ currently being called as the target of the cli thread creation
    """

    print(f"this is {__name__} probably headwaters.fast_engine.fast")

    # create a tuning_q here

    threads = []

    num_thr = 1

    for _ in range(num_thr):
        worker = Worker(emit_q) # passes the emit_q in object init, so not needed as args to thread
        threads.append(threading.Thread(target=worker.generate)) # pass tuning_q

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()