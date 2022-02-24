import random


class Words:
    def __init__(self):
        self.name = "words"
        self.error_mode = False
        self.error_probability = 0.3
        self.library = ["avocado", "banana", "cherry", "dates", "elderberries"]
        self.errors = [1.87392, True, None]

    def get_event(self):
        """standard getter method for every domain class"""

        if self.error_mode:
            prob = random.randint(1, 10) / 10
            if prob <= self.error_probability:
                event = {"domain": "words", "value": random.choice(self.errors)}
            else:
                event = {"domain": "words", "value": random.choice(self.library)}
            return event
        else:
            event = {"domain": "words", "value": random.choice(self.library)}
            return event

    def set_word(self, new_word):
        """setter to add a word to the library
        
        to be directly called from the http route is the idea...

        """
        self.library.append(new_word)
        print(self.library)
        return f"added {new_word}"
