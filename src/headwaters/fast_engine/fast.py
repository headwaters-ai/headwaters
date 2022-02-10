import threading
import random
import time

"""I think this will become an object that holds its state of things
like frequency, and event scheme, which can be accessed and set"""

def generator(emit_q):
    """ this is an example of the deep generator part of each engine, called by the specfici egnine mgr below"""
    while True:
        item = {
            "topic": "speedyfastness",
            "payload": random.random()
        }
        emit_q.put(item)

        # for example, this param of time.sleep is how frequency would be controlled...
        # should this happen at the worker level or up at the mgr?
        time.sleep(random.random())

def mgr(emit_q):

    """ this is an example of the top level entry point to each domain engine, will be moreness
    
    lots of shit can happen here, spawn threads, create dbs, import bits and bobs etc

    """

    print(f"this is {__name__} probably headwaters.fast_engine.fast")

    threads = []

    num_thr = 1

    for _ in range(num_thr):
        threads.append(threading.Thread(target=generator, args=(emit_q,)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()