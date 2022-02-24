import random


class Words:
    def __init__(self):
        self.name = 'words'
        self.library = [
            "avocado",
            "banana",
            "cherry",
            "dates",
            'elderberries'
        ]

    def get_event(self):
        """standard getter method for every domain class"""
        event = {
            'domain': 'words',
            'value': random.choice(self.library)
            }
        return event