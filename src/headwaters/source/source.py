import pandas as pd
import random
import pkgutil
import json
import logging

# from .source_schemas import fruits


class Source:

    """
    This needs to be passed just a string indictaing the source method,
    and the instance needs to grab the data and schema from the right place
    using the pckg data...

    """

    def __init__(self, source_name):

        if not isinstance(source_name, str):
            raise ValueError(
                f"ValueError: 'source_name' parameter must be a string, passed method was {type(source_name)}"
            )

        supported_models = [
            "fruit_sales",
        ]

        if source_name not in supported_models:
            raise ValueError(
                f"ValueError: passed 'source_name' of {source_name} is not supported"
            )

        self.name = source_name

        self.get_schema()

    def get_schema(self):
        """use pkgutil to resolve and load the schema for the passed source_name

        expects a json config file at the mo'
        """
        try:
            initial_schema = pkgutil.get_data(
                "headwaters", f"/source/schemas/{self.name}.json"
            )
        except:
            raise

        initial_schema = json.loads(initial_schema)

        self.schema = initial_schema["schema"]
        self.data = initial_schema["data"]
   
    def new_event(self):
        """create a new event based on instructions in the schema"""

        new_event = {}

        for k, v in self.schema.items():
            if k == "_select_from":
                for sk, sv in v.items():
                    if sv["method"] == "rand_choice":
                        
                        new_event_data = []
                        _selected_data = []

                        if sv["select_quantity"] == "one":
                            _selected_data.append(random.choice(self.data[sk]))
                        elif sv["select_quantity"] == "many":
                            for _ in range(random.randint(2,10)):
                                _selected_data.append(random.choice(self.data[sk]))

                        if sv["choose_keys"]:
                            chosen_keys = sv["choose_keys"]
                            for s in _selected_data:
                                new_event_data.append({nk: nv for nk, nv in s.items() if nk in chosen_keys})
                        else:
                            for s in _selected_data:
                                new_event_data.append(s)  
                                    
                        if sv["select_quantity"] == "one":
                            if sv["spread_keys"]:
                                new_event.update(new_event_data[0])
                            else:
                                new_event[sk] = new_event_data[0]
                        elif sv["select_quantity"] == "many":
                            if sv["spread_keys"]:
                                for x in new_event_data:
                                    new_event.update(x)
                            else:
                                new_event.update({sk: new_event_data})
                continue
    
            if v["method"] == "rand_int":
                new_int = random.randint(v["rand_min"], v["rand_max"])
                if v["insert_to"]:
                    for destination in v["insert_to"]:
                        if not self.schema["_select_from"][destination]["spread_keys"]:
                            for line in new_event[destination]:
                                line.update({k:new_int})
                        else:
                            print("handle error here")
                else:
                    new_event[k] = new_int


            # random_float, rnad_address, rand_name, rand_age, rand_bool, incr_from_prev, decr_from_prev
            # etc from faker or generated

        return new_event
