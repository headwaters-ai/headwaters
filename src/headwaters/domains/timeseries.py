import random


class Timeseries:
    def __init__(self):
        self.name = 'timeseries'

    def get_event(self):
        """standard getter method for every domain class"""
        event = {
            'domain': 'timeseries',
            'value': random.random()
            }
        return event
