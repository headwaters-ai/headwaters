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
        """run some basic checks agsint type and value of passed source_name"""

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

        # once checks pass, go and grab the relevant data
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

            # just bubbling the error up right now, this will need to change
            raise

        initial_schema = json.loads(initial_schema)

        self.schema = initial_schema["schema"]
        self.data = initial_schema["data"]
        self.errors = initial_schema["errors"]

    def new_event(self):
        """create a new event based on instructions in the schema"""

        new_event = {}

        print(f"NEW EVENT")
        print("______________________________")
        for k, v in self.schema.items():

            # k is "_select_from", v is dict with keys product and customer
            if k == "_select_from":
                # DATA SELECTION ZONE
                for data_name, settings in v.items():
                    print(f"START {data_name} processing:")
                    # start with:
                    _selected_list = []  # choise from data goes here
                    # replaced by:
                    _filtered_list = []  # chosen keys placed here
                    # then loop _filtered to add value_errors
                    _filtered_error_list = []
                    # which is then assigned to new_event as the value of the key 'data_name'


                    if settings["select_method"] == "rand_choice":

                        # the config file options for rand_choice can be either an int or a 'many' string

                        # in the case of an int
                        if isinstance(settings["select_quantity"], int):
                            # loop through the data that number of times
                            # for that data_name
                            for _ in range(settings["select_quantity"]):

                                # this is the main guts of the selection of existing


                                _selected_list.append(
                                    random.choice(self.data[data_name])
                                )

                        # in the case of the 'many' string:
                        if settings["select_quantity"] == "many":
                            # we need to know the length of the data, then can use that
                            # as the max for a randint to use as the range max:
                            range_max = len(self.data[data_name])

                            for _ in range(random.randint(1, range_max)):
                                _selected_list.append(
                                    random.choice(self.data[data_name])
                                )

                    print(f"{data_name}{_selected_list = }")
                    print()

                    # KEY FILTERING

                    if settings["choose_keys"]:

                        chosen_keys = settings["choose_keys"]
                        for s in _selected_list:

                            # could actually generate keys errors here?
                            _filtered_list.append(
                                {nk: nv for nk, nv in s.items() if nk in chosen_keys}
                            )
                    else:
                        _filtered_list = _selected_list

                    print(f"{data_name}{_filtered_list = }")
                    print()


                    # ERROR MODE ZONE

                    # _selecte d_list is avaibal ehere pre key selection
                    # for now assuming single depth dicts in the list, this is a MAJOR
                    # assumption and needs to be solved with some simple recursive finder funcs

                    # i know which area of schema we are in here becuase we are behing the 
                    # "_select_from" if guard

                    # is the error_mode of value_errors active?
                    if "value_errors" in self.errors['modes']:
                    # if so, get value_errors from settings
                        value_errors = self.schema[k][data_name]["value_errors"]

                        # check if there are value_errors sspecified:
                        # only make amednments to values if there are value_errors to apply
                        if value_errors:
                            # go through every line dict in the selection
                            # as we know MAJOR ASSUMPTION HERE
                        
                            for _item in _filtered_list:

                                print(f"item in {data_name}: {_item}")

                                # the first approach is to apply a value_error to a random key in EACH
                                # item of the selected list
                                # there may be more approaches in the future

                                # so, select a random key from the dict
                                random_key = random.choice(list(_item.keys()))
                                print(f"{random_key =}")
                                
                                the_random_value = _item[random_key]
                                print(f"{the_random_value = }")
                            
                                
                                if "type" in value_errors:
                                    # apply type error to the random key

                                    type_dict = {
                                        str: 'string error, £ ?',
                                        int: 42, # replace with random call
                                        float: 1.9876542, # replace with random call 
                                        bool: True # randomise
                                    }
                                    
                                    # get the type of the_random_value
                                    type_of_random_value = type(the_random_value)
                                    print(f"the type of the random value: {type_of_random_value}")

                                    # remove the type of the random value from the list of types
                                    type_dict.pop(type_of_random_value)
                                    print(f"the type dict after editing: {type_dict}")

                                    # remove random key from _item dict to be replaced with error_item
                                    _item.pop(random_key)
                                    print(f"item with value removed: {_item}")
                                    
                                    # replace with same random key but select a new error val from type dict
                                    _item.update({random_key: type_dict[random.choice(list(type_dict.keys()))]})
                                    print(f"recombined _itme but with error value: {_item}")

                                    # add the new error filled item into the _filtered_error_list
                                    _filtered_error_list.append(_item)


                                print()



                                if "range" in value_errors:
                                    pass
                                    # print(f"this is on the range")
                                # will need a way to handle erroor types here
                                # could use list of 'value_error_styles' in schema
                            
                        else:
                            _filtered_error_list = _filtered_list        

                    else:
                        _filtered_error_list = _filtered_list
                   



                    # then create out this data_name part of the new_event
                    _this_data_name_dict = {data_name: _filtered_error_list}
                    # print(_this_data_name_dict)
                    # print()

                    # then append this speciffc dict for the data_name into the main new_event dict
                    new_event.update(_this_data_name_dict)
                    print()
                    print(f"new_event after selection, filtering and errors: {new_event}")
                    print()

            # this is the main creation section
            # where the _select_from key has not been hit, so every other key will hit this
            # will be processed in this section
            # per data_name
            else:
                # DE NOVO CREATION ZONE
                # so can use the v["accessor"] to access the settings, rename for clarity
                data_name = k
                settings = v

                if settings["create_method"] == "rand":  # it will be for now

                    # 1 create the new_value for the data_name first
                    #   considtioally check for type
                    #   create new 
                    # 2 then apply error logic
                    # 3 then either insert into a destinaiton in the new_event or in at top level

                    


                    # check if error_mode is activated globally for this source:
                    if "value_errors" in self.errors['modes']:

                        pass

                    else:
                        # straight up just create the new value for data_name with no errors
                        # here coule create and just pass to a private error method encapsualting 
                        # error stuff from above for exisitng data YES DO THIS
                            # check this all works before a refactor like that for now
                        pass

                    if settings["insert_into"]:
                        # let's guard just to check the new_event has been created
                        if new_event:
                            # now, here we are going to have a list of one or more target
                            # keys/fields we want to insert into.
                            # let's get those:
                            insert_destinations = settings["insert_into"]  # it's a list

                            # lets loop thought the list and pull out each insert destination
                            for insert_destination in insert_destinations:

                                # the insert destination in the new_event data has
                                # one or more lines in it
                                # within the new_event
                                # every one of these lines is a dict
                                for line_dict in new_event[insert_destination]:
                                    # this line_dict is what we will want to add the new_int into
                                    
                                    
                                    # update the line_dict
                                    line_dict.update(self._create_new(data_name))

                    else:
                        
                        new_event.update(self._create_new(data_name))

        # FLATTENING ZONE
        # after the new_event has been formed and created data has been inserted
        # this is when any flattening can happen to shape the final new_event
        # flatten is a bool

        # let's get every key in the _select_from part of the config file into a list
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

        print("_____________________")
        print()

        # print("new_event = ", json.dumps(new_event, indent=4))

        
        return new_event

    def _create_new(self, data_name) -> dict:
        """ create a new value for a supplied data_name (ie the top_level key of
        self.schema which is not '_select_from') and return a dict of shape:
        
            {data_name: new_value}
        
        """
        settings = self.schema[data_name]

        if settings['create_type'] == 'int':
            # check for creation settings else just plug some defaults
            # defaults:
            int_min = -100
            int_max = 100
            
            # overwrite defaults if present
            if 'int_min' in settings.keys():
                int_min = settings['int_min']
            if 'int_max' in settings.keys():
                int_max = settings['int_max']

            # check value of int_min and max
            if int_max <= int_min:
                raise ValueError(f"supplied int_max of {int_max} must be greater than int_min of {int_min}")

            new_value = random.randint(int_min, int_max)

        elif settings['create_type'] == 'float':
            pass
        elif settings['create_type'] == 'str':
            pass
        elif settings['create_type'] == 'bool':
            pass
        # more and more types here, up to faker integraiton
        elif settings['create_type'] == 'address':
            pass
        else:
            pass

        new_value_dict = {data_name: new_value}

        return new_value_dict
