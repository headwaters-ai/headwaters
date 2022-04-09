from hashlib import new
from textwrap import indent
import pandas as pd
import random
import pkgutil
import json
import uuid
import logging

class Source:

    """
    This needs to be passed just a string indictaing the source method,
    and the instance needs to grab the data_name and schema from the right place
    using the pckg data_name...

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
        # print(json.dumps(self.schema, indent=4))
   
    def new_event(self):
        """create a new event based on instructions in the schema"""

        new_event = {}

        for k, v in self.schema.items():

            # k is "_select_from", v is dict with keys product and customer
            if k == "_select_from":
                for data_name, settings in v.items():

                    # start with:
                    _selected_list = [] # choise from data goes here
                    # replaced by:
                    _filtered_selected_list = [] # chosen keys placed here

                    if settings["select_method"] == "rand_choice":

                        # the config file options for rand_choice can be either an int or a 'many' string

                        # in the case of an int
                        if isinstance(settings["select_quantity"], int):
                            # loop through the data that number of times 
                            # for that data_name
                            for _ in range(settings["select_quantity"]):
                                _selected_list.append(random.choice(self.data[data_name]))

                        # in the case of the 'many' string:
                        if settings["select_quantity"] == "many":
                            # we need to know the length of the data, then can use that
                            # as the max for a randint to use as the range max:
                            range_max = len(self.data[data_name])

                            for _ in range(random.randint(1, range_max)):
                                _selected_list.append(random.choice(self.data[data_name]))
                    
                    # print(f"{_selected_list = }")
                    
                    if settings["choose_keys"]:

                        chosen_keys = settings["choose_keys"]
                        for s in _selected_list:
                            _filtered_selected_list.append({nk: nv for nk, nv in s.items() if nk in chosen_keys})
                    else:
                        _filtered_selected_list = _selected_list

                    # print(f"{_filtered_selected_list = }")

                    # then create out this data_name part of the new_event
                    _this_data_name_dict = {data_name: _filtered_selected_list}
                    # print(_this_data_name_dict)
                    # print()

                    # then append this speciffc dict for the data_name into the main new_event dict
                    new_event.update(_this_data_name_dict)
            
            # this is the main creation section
            # where the _select_from key has not been hit, so every other key will hit this
            # will be processed in this section
            # per data_name
            else:
                # so can use the v["accessor"] to access the settings, rename for clarity
                data_name = k
                settings = v
                
                if settings["create_method"] == "rand_int": # it will be for now
                    
                    if settings["insert_into"]:
                        # let's guard just to check the new_event has been created
                        if new_event:
                            # now, here we are going to have a list of one or more target
                            # keys/fields we want to insert into.
                            # let's get those:
                            insert_destinations = settings["insert_into"] # it's a list

                            # lets loop thought the list and pull out each insert destination
                            for insert_destination in insert_destinations:

                                # the insert destination in the new_event data has 
                                # one or more lines in it
                                # within the new_event
                                # every one of these lines is a dict
                                for line_dict in new_event[insert_destination]:
                                    # this line_dict is what we will want to add the new_int into
                                    # create the new_int
                                    new_int = random.randint(settings["rand_min"], settings["rand_max"])
                                    _this_data_name_dict = {data_name: new_int}
                                    # update the line_dict
                                    line_dict.update(_this_data_name_dict)

                    else:
                        # this is the straght up, create a new int once and 
                        # add it with its data_name
                        # to the new_event
                        new_int = random.randint(settings["rand_min"], settings["rand_max"])
                        _this_data_name_dict = {data_name: new_int}

                        new_event.update(_this_data_name_dict)

        # after the new_event has been formed and created data has been inserted
        # this is when any flattening can happen to shape the final new_event
        # flatten is a bool

        #let's get every key in the _select_from part of the config file into a list
        data_names = list(self.schema["_select_from"].keys())

        # check if the data_name has a true flatten param
        for data_name in data_names:
            if self.schema["_select_from"][data_name]["flatten"]:
                # the config file is true to flatten, the work happens here
                # fuck, nested dict may need a recursive algo here.... :|
                # but, for now, let's assume single level

                # we cannot flatten an object with more than one entry
                # two ways to check, check data or the config file
                # to check len == 1
                # let's assume the config translates to the actual data for now

                if self.schema["_select_from"][data_name]["select_quantity"] == 1:

                    # we need to reach in and grab the single dict from the new_event data
                    # with the key of the data_name
                    this_dict = new_event[data_name]

                    # then for each element of this_dict we need to update the top level
                    # of new_event, then delete the key
                    for this_dict_element in this_dict:
                        new_event.update(this_dict_element)
                    # once all the elements have been squirrelled to the top level, delete the key
                    new_event.pop(data_name, None)

                else:
                    # do nothing..
                    # or should i raise an error to advise??
                    pass
                
            else:
                # we just do nothing
                pass



        # add a cheeky wee uuid for fun
        new_event.update({"event_id": str(uuid.uuid4())})

        # print("new_event = ", json.dumps(new_event, indent=4))

        # error mode support:
        
        # a new_event looks like this:
        # {
        #     "products": [
        #         {
        #             "item_name": "cherries",
        #             "item_price": 3.5,
        #             "sku": 34567,
        #             "volume_sold": 7
        #         },
        #         {
        #             "item_name": "damsons",
        #             "item_price": 1.2,
        #             "sku": 45678,
        #             "volume_sold": 1
        #         },
        #         {
        #             "item_name": "cherries",
        #             "item_price": 3.5,
        #             "sku": 34567,
        #             "volume_sold": 7
        #         },
        #         {
        #             "item_name": "cherries",
        #             "item_price": 3.5,
        #             "sku": 34567,
        #             "volume_sold": 7
        #         }
        #     ],
        #     "shops": [
        #         {
        #             "shop_id": 2,
        #             "address": "506 St John's Road",
        #             "has_fridges": true
        #         }
        #     ],
        #     "timestamp": 12200790,
        #     "customer_id": 98765,
        #     "cust_name": "Ben",
        #     "event_id": "a6570e34-0933-4c7f-9a6d-aaa413dc8a10"
        # }

        # next plan is to inject value errors when values are selected or created
        
        # and to then create, remove or mash-up keys on the new_event after new_event is made fully

        return new_event
            # random_float, rnad_address, rand_name, rand_age, rand_bool, incr_from_prev, decr_from_prev
            # etc from faker or generated
