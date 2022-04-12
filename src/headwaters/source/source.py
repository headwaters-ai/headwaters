import random
import pkgutil
import json
import uuid
from datetime import datetime


class Source:

    """
    This needs to be passed just a string indictaing the source method,
    and the instance needs to grab the field_name and schema from the right place
    using the pckg field_name...

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
        self._load_schema()

    def _load_schema(self):
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
        self.existing_data = initial_schema["data"]
        self.errors = initial_schema["errors"]

    def new_event(self):
        """public method to create a new event based on the schema of the class instance"""

        self.new_event_data = {}

        start = datetime.now()
        # print(f"NEW EVENT")
        # print("______________________________")
        # print()

        # CALLING ORDER
        # the flow of method calls in new_event is intended to build up the
        # self.new_event_data incrementally, so order matters.

        # Stage 1 - creating the data
        # ____________________________

        # 1.1 selection or creation call
        for field_name, field_settings in self.schema.items():

            if field_settings["existing"]:
                self.new_event_data.update(self._select_existing(field_name))
            else:
                self.new_event_data.update(self._create_new(field_name))

        # 1.2 filtering call
        for event_name in self.new_event_data.keys():

            self.new_event_data.update(self._filter_keys(event_name))

        # 1.3 value errors call

        for event_name in self.new_event_data.keys():

            self._create_value_errors(event_name)

        # Stage 2 - shaping the data
        # __________________________

        # 2.1 insertion call
        # take a snapshot of new_event_data keys at this point
        list_of_event_names = list(self.new_event_data.keys())
        # then loop through those to avoid a 'dict changed shape during iteraiton' error
        for event_name in list_of_event_names:
            self._insert_into(event_name)

        # 2.2 de-deuplicate keys call
        # from created data and insertion process
        # pass the whole self.new_event_data object
        # & receive back amaended object and assign
        self.new_event_data = self._flatten_duplicate_sub_keys(self.new_event_data)

        # 2.3 flattening call
        # take a snapshot of new_event_data keys at this point
        list_of_event_names = list(self.new_event_data.keys())
        # then loop through those to avoid a 'dict changed shape during iteraiton' error
        for event_name in list_of_event_names:
            # self._flatten() operates diractly on state within the method
            self._flatten(event_name)

        # 2.4 key errors call

        self._create_key_errors()

        # add a cheeky wee uuid at top level
        self.new_event_data.update({"event_id": str(uuid.uuid4())})

        # pop output to console for debugging and dev only
        # print(json.dumps(self.new_event_data, indent=4))
        # print()
        end = datetime.now()

        print(f"new_event call duartion = {end - start}")

        return self.new_event_data

    def _select_existing(self, field_name: str) -> dict:

        """Given the field_name to search the schema for,
        check the 'select_method' and
        'select_quantity' of the schema and return a dict keyed by field_name and value of
        a list of selected items from self.existing_data of shape:

        ..code-block:: python


            {
                'field_name': [
                    {field_name: new_value},
                    ...
                ]
            }
        :param field_name: the field_name is the key of the self.schema dictionary ``self.schema[field_name]``

        :returns: dict keyed by ``field_name`` with value set as a list of dicts of generated new items
        """

        field_settings = self.schema[field_name]

        output_values = []

        if field_settings["select_method"] == "rand_choice":

            # the config file options for rand_choice can be either an int or a 'many' string

            # in the case of an int
            if isinstance(field_settings["select_quantity"], int):
                # loop through the data that number of times
                # for that field_name
                for _ in range(field_settings["select_quantity"]):

                    # this is the main guts of the selection of existing
                    output_values.append(random.choice(self.existing_data[field_name]))

            # in the case of the 'many' string:
            if field_settings["select_quantity"] == "many":
                # we need to know the length of the data, then can use that
                # as the max for a randint to use as the range max:
                range_max = len(self.existing_data[field_name])

                for _ in range(random.randint(1, range_max)):
                    output_values.append(random.choice(self.existing_data[field_name]))
        return_shape = {field_name: output_values}

        return return_shape

    def _create_new(self, field_name: str) -> dict:
        """create a new value for a supplied field_name (ie the top_level key of
        ``self.schema``) and returns a dict of a list of dicts keyed by ``field_name``:

        ..code-block:: python

            {
                'field_name': [
                    {field_name: new_value},
                ]
            }

        the quantity of items in the list is controlled by the 'create_volume' setting.

        :param field_name: the ``field_name`` is the key of the self.schema dictionary ``self.schema[field_name]``

        :returns: dict keyed by ``field_name`` with value set as a list of dicts of generated new items
        """
        settings = self.schema[field_name]
        output_values = []

        try:
            create_volume = settings["create_volume"]
        except KeyError:
            # use KeyError like Flask does to guard against missing keys
            create_volume = 1

        for _ in range(create_volume):

            if settings["create_type"] == "int":
                # check for creation settings else just plug some defaults
                # defaults:
                int_min = -100
                int_max = 100

                # overwrite defaults if present
                if "int_min" in settings.keys():
                    int_min = settings["int_min"]
                if "int_max" in settings.keys():
                    int_max = settings["int_max"]

                # check value of int_min and max
                if int_max <= int_min:
                    raise ValueError(
                        f"supplied int_max of {int_max} must be greater than int_min of {int_min}"
                    )

                new_value = random.randint(int_min, int_max)

            elif settings["create_type"] == "float":
                pass
            elif settings["create_type"] == "str":
                pass
            elif settings["create_type"] == "bool":
                pass
            # more and more types here, up to faker integraiton
            elif settings["create_type"] == "address":
                pass
            else:
                pass

            new_value_dict = {field_name: new_value}
            output_values.append(new_value_dict)

        return_shape = {field_name: output_values}

        return return_shape

    def _filter_keys(self, field_name: str) -> dict:
        """call on each field_name in self.new_event_data and filters to only keys specified

        returns a dict of a list of dicts keyed by ``field_name``:

        ..code-block:: python

            {
                'field_name': [
                    {field_name: new_value},
                ]
            }

        the quantity of items in the list is controlled by the 'create_volume' setting.

        :param field_name: the ``field_name`` is the key of the self.schema dictionary ``self.schema[field_name]``

        :returns: dict keyed by ``field_name`` with value set as a list of dicts of generated new items
        """

        settings = self.schema[field_name]
        field_values = self.new_event_data[field_name]

        output_value = []

        try:
            chosen_keys = settings["choose_keys"]
        except KeyError:
            chosen_keys = None  # or raise?

        for line in field_values:

            if chosen_keys:
                output_value.append({k: v for k, v in line.items() if k in chosen_keys})
            else:
                output_value.append(line)

        return_shape = {field_name: output_value}
        return return_shape

    def _insert_into(self, field_name) -> None:

        # lets grab the list of insert destinations from the schema
        try:
            insert_destinations = self.schema[field_name]["insert_into"]
        except KeyError:
            insert_destinations = False

        if insert_destinations:
            # if there are destinations, looping through them will give us the key
            # to use to reach into self.new_event_data and add the field
            for insert_destination in insert_destinations:

                # need to check that the value of the self.new_event_data[insert_destination]
                # ie where the new data is going, is a list so it can have a len
                # where self.new_event_data[insert_destination] is a top level key, the value
                # is just an int, float, bool, str etc
                # which has no len
                if isinstance(
                    self.new_event_data[insert_destination], list
                ) and isinstance(self.new_event_data[field_name], list):
                    # if the len of the insert dest is > 1
                    # then _create_new needs to be recalled for num times == len(insert dest)
                    if len(self.new_event_data[insert_destination]) > 1:
                        for item in self.new_event_data[insert_destination]:
                            item.update(self._create_new(field_name))

                    # if the len of the insert dest is == 1
                    # insert the created field as is
                    else:
                        for item in self.new_event_data[insert_destination]:
                            # get the data we want to insert which is somewhere else in the new_event_data
                            data_to_insert = self.new_event_data[field_name]

                            # then update the item with the new data to insert
                            item.update({field_name: data_to_insert})
                            # this will be flattened during the call to _flatten_duplicate_sub_keys call
            self.new_event_data.pop(field_name)

    def _flatten_duplicate_sub_keys(self, parent: dict) -> dict:
        """this purpose of this method is to:

        - traverse the arbitary depth of a passed dict object ``parent``
        - identify any duplicate keys in sub dicts
        - flatten the key to the ``parent`` level and therefore remove the duplicate

        An assumption for now is that any dict that itself holds one or more dicts
        as values holds them in a list and that the shape
            ``{"key": {"key": value}}``
        will not exist, instead the shape
            ``{"key": [{"key": value}]}``
        is expected to exist.

        """

        if isinstance(parent, dict):
            for key in parent.keys():
                if isinstance(parent[key], list):
                    if len(parent[key]) == 1:
                        item_list = []
                        for item in parent[key]:
                            item_list.append(item)

                        item_keys = []
                        for d in item_list:
                            for k, v in d.items():
                                item_keys.append(k)

                        # print(f"{key}: {item_list = }")

                        # print(f"{key} duplicate: {key in item_keys}")

                        if key in item_keys:
                            # print(f"execute change here")
                            new_val = parent[key][0]
                            parent.update(new_val)
                            # print(f"{parent}")

                    self._flatten_duplicate_sub_keys(parent[key])

        elif isinstance(parent, list):
            for item in parent:
                # print(f"items: {item.keys()}")
                self._flatten_duplicate_sub_keys(item)

        else:
            pass

        return parent

    def _flatten(self, field_name: str) -> None:
        """Call on each fiedl name in new_event_data

        This method operates directly on ``self.new_event_data``, unlike other methods
        this is because i cannot think how to effectively update keys upward to the parent
        and delete the old child key from the parent without operating within a loop of items

        the other option would be to have a static class method, and pass and return new_event,
        but that seems kind of like disconnecting then reconnecing the logic of this
        method from the state of the class.

        see pseudocode workings for a standalone function, not a class method, so the change
        is thet use of ``self.new_event_data`` in place of ``parent``

        Unsure if this the right decision, but will roll with for now.

        ..code-block:: python:

            def flatten(parent, child_key):
                if len(parent[child_key]) > 1:
                    return parent
                else:
                    outlist = []
                    for item in parent[child_key]:
                        parent.update(item)
                    parent.pop(child_key)

                    return parent

            result = flatten(new_event, "customers")

        """

        # assess if the flatten settings bool is true
        try:
            flatten = self.schema[field_name]["flatten"]
        except KeyError:
            flatten = False

        if flatten:
            if isinstance(self.new_event_data[field_name], list):
                if len(self.new_event_data[field_name]) > 1:
                    # just do nothing
                    pass
                else:
                    # operate on self.new_event_data directly
                    for item in self.new_event_data[field_name]:
                        # egress the item key to reference to stop duplicated keys popping
                        item_key = list(item.keys())[0]
                        self.new_event_data.update(item)

                    # this little jiggery pokery below is to guard against when a
                    # created field duplicates it's key and is of form:
                    #     {
                    #         'volume_sold': [
                    #             {'volume_sold': 12}
                    #         ]
                    #     }
                    # it will be flattened to:
                    #     {
                    #         'volume_sold': 12
                    #     }
                    # but then dict.pop('volume_sold') is called becuase the existing data approach has different
                    # key in the list of dicts form the field_name itself, so the approach is to pop 'field_name'
                    # so i don't want to pop field_name if it matches the key of the item being flattened
                    # If you don't protect like this, the key pops itself after the update call...
                    # It's probably bad form in the way created events are being created, but the
                    # form currently works for other method calls and reasons, so I'm keeping like it
                    # is until it causes further issues
                    if item_key != field_name:
                        self.new_event_data.pop(field_name)

    def _create_value_errors(self, field_name):
        """The purpose of this method is to:

        - find the ``value_errors`` list of the param ``field_name`` in ``self.schema``
            - this is currently being called at an early stage of the new_event process
            therefore the top level keys of ``self.new_event_data`` - which are what
            are being passed as ``field_name`` - will still reflect
            those of ``self.schema``

        - based on the error setting found for that key, fuck the data ''value'' up
        - replace the new value in place of the old value



        """

        # ``self.errors`` specifies the active error mode as includign value_errors
        if self.errors["value_errors"]:
            if random.random() < self.errors["value_error_freq"]:
                for value_error in self.schema[field_name]["value_errors"]:
                    if value_error == "type":

                        # at this stage in the new event process we know
                        # that each field_name in the new event data has a list of more dicts.
                        # this assumption of calling order and initial shape is either something
                        # of great horror or isn't an issue. Time will tell. Feels sketchy.
                        for item in self.new_event_data[field_name]:

                            # choosing a random key to mess up the value of feels a good first
                            # methodology. I'd imagine a lot of time and refactoring is going to
                            # happen here.
                            random_key = random.choice(list(item.keys()))

                            # get the current value of that random key and infer it's type
                            curr_value = item[random_key]
                            curr_value_type = type(curr_value)

                            type_dict = {
                                str: "string error, £ ?",
                                int: 42,  # replace with random call, or faker
                                float: 1.9876542,  # replace with random call, or faker
                                bool: True,  # randomise
                            }

                            # edit the type dict to remove the current value's type
                            type_dict.pop(curr_value_type)

                            # randomly choose a value from the type_dict to replace the
                            # current value of the item
                            new_error_value = type_dict[
                                random.choice(list(type_dict.keys()))
                            ]
                            item.update({random_key: new_error_value})

        else:
            pass

    def _create_key_errors(self):
        # keep this simple
        # good opp to test probaility concept
        # just pass across the top level keys of new event and
        # based on probablity, either drop or change. Could add but lets see

        # check key erro mode is active
        if self.errors["key_errors"]:
            if random.random() < self.errors["key_error_freq"]:
                key_list = list(self.new_event_data.keys())

                chosen_key = random.choice(key_list)
                # embracing randomness to either drop or mess with key
   
                if random.random() >= 0.5:
                    self.new_event_data.pop(chosen_key)
                else:
                    messed_up_key = chosen_key[:len(chosen_key)-2]
                    self.new_event_data[messed_up_key] = self.new_event_data[chosen_key]
                    self.new_event_data.pop(chosen_key)


        else:
            pass

