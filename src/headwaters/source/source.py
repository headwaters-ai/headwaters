import random
import pkgutil
import json
from json.decoder import JSONDecodeError
import uuid
from datetime import datetime
from copy import deepcopy


class Source:

    """
    The Source class provides the mechanism to create a ``new_event`` from existing
    data, freshly created data, or a combination of both. Class attribute dictionaries
    of ``self.config["schema"]``, ``self.config["errors"]`` and ``self.existing`` are loaded from a
    config file at instantiation and control the initial characteristics of
    the ``new_event``. Public getter and setters provide methods to change the
    character of a ``new_event`` enabling changes to all aspects of the
    Source instance during server runtime.

    A Source class instance is created by the Server and passed into an instance
    of a Stream class which schedules the calls to ``new_event()``.

    Core characteristics that are controllable are:

        - selection from supplied existing data:
            - random choice of n or "many" records per event
            - filtering of keys chosen from existing data
        - creation of new data:
            - randomised
            - append to existing and read-from-last
            - insertion of newly created data into selected existing data
        - generation of errors in the new event:
            - key errors:
                - drop key
                - mangle key
            - value errors:
                - type errors
            - controllable probability of error occurence

    '''Instantiation'''

    The Source class expects one argument ``source_name``. This must match a provided schema config json
    file located in ``'./schemas/'``. If the Source class cannot resolve ``source_name`` it raises
    a ``FileNotFoundError`` upward.

    '''Public Instance Methods'''

        - ``new_event()``:
    """

    def __init__(self, source_name: str):
        """Create a new instance of a Source class.

        :param source_name: the name of the source data for which a schema
        config file exists, required.
        :type source_name: string

        """

        if not isinstance(source_name, str):
            raise ValueError(
                f"ValueError: 'source_name' parameter must be a string, passed method was {type(source_name)}"
            )

        supported_sources = [
            "fruit_sales",
        ]

        if source_name not in supported_sources:
            raise ValueError(
                f"ValueError: passed 'source_name' of {source_name} is not supported"
            )

        # attributes
        self.name = source_name

        # once checks pass, go and grab the relevant data
        self._load_schema()

    def _load_schema(self) -> None:
        """use pkgutil to resolve and load the schema for the passed source_name

        expects a json config file.
        """

        try:
            initial_config = pkgutil.get_data(
                "headwaters", f"/source/schemas/{self.name}.json"
            )
        except:
            # just bubbling the error up right now, this will need to change
            raise

        try:
            initial_config = json.loads(initial_config)
        except JSONDecodeError:
            raise ValueError(
                f"error parsing json config file for {self.name}, is there an error in the {self.name}.json file?"
            )

        self.config = initial_config

    def new_event(self) -> dict:
        """Create and return a ``new_event`` dictionary object according to the
        settings in attributes ``self.config["schema"]`` and ``self.config["errors"]``

        :returns: dictionary of the ``new_event``

        """

        self.new_event_data = {}

        # print(f"NEW EVENT")
        # print("______________________________")
        # print()

        # CALLING ORDER
        # the flow of method calls in new_event is intended to build up the
        # self.new_event_data incrementally, so order matters.

        # Stage 1 - creating the data
        # ____________________________

        # 1.1 selection or creation call
        for a, b in self.config["schema"].items():

            if b["existing"]:
                self.new_event_data.update(self._select_existing(a))
            else:
                self.new_event_data.update(self._create_new(a))

        # 1.2 filtering call
        for c in self.new_event_data.keys():

            self.new_event_data.update(self._filter_keys(c))

        # 1.3 value errors call
        if self.config["error_mode"]["value_errors"]:
            for d in self.new_event_data.keys():

                self.new_event_data.update(self._create_value_errors(d))

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

        # print(self.new_event_data["event_id"])
        # print("___________________")
        # print()
        return self.new_event_data

    def _select_existing(self, field_name: str) -> dict:

        """Given the field_name to search the schema for,
        check the 'select_method' and
        'select_quantity' of the schema for that ``field_name`` and return a
         dict keyed by field_name with value of
        a list of selected dict items from ``self.config["data"]``.

        :param field_name: 'field_name' is the key of the
        ``self.config["schema"]`` dictionary like this: ``self.config["schema"][field_name]``

        :returns: dict keyed by ``field_name`` with value set as a list of
        dicts of generated new items of shape:

        ..code-block:: python

            {
                'field_name': [
                    {field_name: new_value},
                    ...
                ]
            }

        """

        field_settings = self.config["schema"][field_name]

        output_values = []

        if field_settings["select_method"] == "rand_choice":

            # the config file options for rand_choice can be either an int or a 'many' string

            existing_data_list = deepcopy(self.config["data"][field_name])

            # get vars for use below
            len_data = len(self.config["data"][field_name])
            select_quantity = field_settings["select_quantity"]
            # in the case of an int
            if isinstance(select_quantity, int):
                

                # this is the main guts of the selection of existing
                # this assumes that the value of each ``field_name`` in
                # existing data is a list. This assumption may not always hold?

                # check select_quantity <= len of data and not negative:
                # or can i rely on inbuilt ValueError from random.sample?

                # return type from random.sample is list, so instead of appending, replace
                # output_values
                try:
                    output_values = random.sample(existing_data_list, k=select_quantity)
                except ValueError as e:
                    raise ValueError(f"the 'select_quantity' value supplied of {select_quantity} created error {e}")

            # in the case of the 'many' string:
            if select_quantity == "many":
                # we need to know the length of the data, then can use that
                # as the max for a randint to use as the range:

                select_quantity = random.randint(1,len_data)

                # return type from random.sample is list, so instead of appending, replace
                # output_values
                output_values = random.sample(existing_data_list, k=select_quantity)

        if field_settings["select_method"] == "from_last":

            # the config file options for rand_choice can be an int not gt len of
            # self.data[field_name]

            existing_data_list = deepcopy(self.config["data"][field_name])

            # in the case of an int, which it has to be?
            if isinstance(field_settings["select_quantity"], int):

                # use slice selectors and supplied int to select n records
                list_len = len(existing_data_list)
                slice_amount = field_settings["select_quantity"]
                selected_list = existing_data_list[list_len - slice_amount :]

                for i in selected_list:
                    output_values.append(i)

        return_shape = {field_name: output_values}

        return return_shape

    def _create_new(self, field_name: str) -> dict:
        """Create a new value for a supplied field_name (ie the top_level key of
        ``self.config["schema"]``) and return a dict of a list of dicts keyed by ``field_name``:

        The quantity of items generated and appended to  the list is
        controlled by the ``create_volume`` setting.

        :param field_name: the ``field_name`` is the key of the
        ``self.config["schema"]`` dictionary ``self.config["schema"][field_name]``

        :returns: dict keyed by ``field_name`` with value set as a
        list of dicts of generated new items of shape:

        ..code-block:: python

            {
                'field_name': [
                    {field_name: new_value},
                ]
            }

        """
        settings = self.config["schema"][field_name]
        output_values = []

        try:
            create_volume = settings["create_volume"]
        except KeyError:
            # use KeyError like Flask does to guard against missing keys
            create_volume = 1

        try:
            build_from = settings["build_from"]
        except KeyError:
            # use KeyError like Flask does to guard against missing keys
            build_from = False

        if build_from:
            # where building off from an exisitng data element
            # outwith creat_volume loop as asusming single for dev now
            # create_methods: incr, decr, walk
            # create types: int, float
            # bool would jsut be a pure de novo insertinto like volume sold
            # string....?

            # grab the settings, need to put behind a try KeyError guard
            create_method = settings["create_method"]
            create_type = settings["create_type"]

            # grab the last record from build from
            # get the location dot string to list elements
            build_from_location_list = build_from.split(".")
            bf_first_key = build_from_location_list[0]
            bf_second_key = build_from_location_list[1]

            data_from_build_from_location = deepcopy(self.config["data"][bf_first_key])
            last_build_from_record = data_from_build_from_location[-1]

            value_to_build_from = last_build_from_record[bf_second_key]
            if create_type == "int":
                if create_method == "incr":
                    new_value = value_to_build_from + settings["incr_by"]
                elif create_method == "decr":
                    new_value = value_to_build_from - settings["decr_by"]
                elif create_method == "walk":
                    walk_val = int(settings["walk_by"])
                    new_value = value_to_build_from + random.randint(
                        (walk_val * -1), walk_val
                    )

            new_value_dict = {bf_second_key: new_value}
            output_values.append(new_value_dict)


        else:
            # pure de novo stuff here
            for _ in range(create_volume):
                if settings["create_method"] == "rand":
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
        """Filter the data selected from existing data
        returns a dict of a list of dicts keyed by ``field_name``:

        :param field_name: the ``field_name`` is the key of the
        ``self.config["schema"]`` dictionary ``self.config["schema"][field_name]``

        :returns: dict keyed by ``field_name`` with value set as a list of dicts
        of generated new items of shape:

        ..code-block:: python

            {
                'field_name': [
                    {field_name: new_value},
                ]
            }
        """

        settings = self.config["schema"][field_name]

        # again, assuming the data shape is a list as expected.
        field_values = self.new_event_data[field_name]

        output_value = []

        try:
            chosen_keys = settings["choose_keys"]
        except KeyError:
            chosen_keys = None

        for line in field_values:

            if chosen_keys:
                output_value.append({k: v for k, v in line.items() if k in chosen_keys})
            else:
                output_value.append(line)

        return_shape = {field_name: output_value}
        return return_shape

    def _insert_into(self, field_name) -> None:
        """Insert newly created data into another top-level key in ``self.new_event_data``
        Operates directly upon the ``self.new_event_data`` attribute object and so does not
        return.

        :param field_name: the field_name of both ``self.config["schema"]`` and ``self.new_event_data``

        """

        # lets grab the list of insert destinations from the schema
        try:
            insert_destinations = self.config["schema"][field_name]["insert_into"]
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
        """De-duplicate keys in newly created data by recursively
        traversing the passed dict object ``parent``, identifying any
        duplicate keys in sub dictionaries if they exist, and then
        flattening the duplicated key to the ``parent`` level.

        Return the newly de-duplicated dict.

        An assumption for now is that any dict that itself holds one or more dicts
        as values holds them in a list and that the shape
            ``{"key": {"key": value}}``
        will not exist, instead the shape
            ``{"key": [{"key": value}]}``
        is expected to exist.

        :param parent: dictionary to traverse

        :returns: dictionary that is deduplicated.
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

                        if key in item_keys:
                            new_val = parent[key][0]
                            parent.update(new_val)

                    self._flatten_duplicate_sub_keys(parent[key])

        elif isinstance(parent, list):
            for item in parent:
                self._flatten_duplicate_sub_keys(item)

        else:
            pass

        return parent

    def _flatten(self, field_name: str) -> None:
        """Flatten values of provided ``field_name`` key to the top level
        of the ``self.new_event_data`` dictionary.

        Does not return

        :param field_name: field_name of object to flatten to top level

        """
        # This method operates directly on ``self.new_event_data``, unlike some other methods
        # this is because i cannot think how to effectively update keys upward to the parent
        # and delete the old child key from the parent without operating within a loop of items

        # the other option would be to have a static class method, and pass and return new_event,
        # but that seems kind of like disconnecting then reconnecing the logic of this
        # method from the state of the class.

        # see pseudocode workings for a standalone function, not a class method, so the change
        # is thet use of ``self.new_event_data`` in place of ``parent``

        # Unsure if this the right decision, but will roll with for now.

        # ..code-block:: python:

        #     def flatten(parent, child_key):
        #         if len(parent[child_key]) > 1:
        #             return parent
        #         else:
        #             outlist = []
        #             for item in parent[child_key]:
        #                 parent.update(item)
        #             parent.pop(child_key)

        #             return parent

        #     result = flatten(new_event, "customers")

        # assess if the flatten settings bool is true
        try:
            flatten = self.config["schema"][field_name]["flatten"]
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

    def _create_value_errors(self, field_name: str) -> dict:
        """Create errors in the ''values'' of ``self.new_event_data['field_name']``
        according to the value error settings
        in ``self.config["schema"][field_name]['value_errors'] if value_error_mode
        is activated globally.

        Uses random float generation to implement simplistic probability of event errors.



        :param field_name: field_name to query both ``self.new_event_data`` and ``self.config["schema"]``

        :returns: dict

        """

        # ``self.config["errors"]`` specifies the active error mode as includign value_errors

        try:
            value_errors_list = self.config["schema"][field_name]["value_errors"]
        except KeyError:
            value_errors_list = False

        if value_errors_list:
            for value_error in value_errors_list:
                if value_error == "type":

                    # at this stage in the new event process we know
                    # that each field_name in the new event data has a list of more dicts.
                    # this assumption of calling order and initial shape is either something
                    # of great horror or isn't an issue. Time will tell. Feels sketchy.
                    r = random.random()
                    s = self.config["error_mode"]["value_error_prob"]

                    original_field_name_item_list = self.new_event_data[field_name]

                    if r < s:

                        random_item = random.choice(original_field_name_item_list)

                        # going to remove random_item from oirignal list, fuck with it, then add it back and update new event again

                        original_field_name_item_list.remove(random_item)

                        # choosing a random key to mess up the value of feels a good first
                        # methodology. I'd imagine a lot of time and refactoring is going to
                        # happen here. That's right!

                        random_key = random.choice(list(random_item.keys()))

                        # get the current value of that random key and infer it's type
                        curr_value = random_item[random_key]
                        curr_value_type = type(curr_value)

                        rand_string = str(uuid.uuid4())[:8]

                        type_dict = {
                            str: rand_string,
                            int: random.randint(
                                -99999999, -777777
                            ),  # replace with random call, or faker
                            float: random.random(),  # replace with random call, or faker
                            bool: True,  # randomise
                        }

                        # edit the type dict to remove the current value's type
                        type_dict.pop(curr_value_type)

                        # randomly choose a value from the type_dict to replace the
                        # current value of the item
                        new_error_value = type_dict[
                            random.choice(list(type_dict.keys()))
                        ]

                        new_error_filled_item = {random_key: new_error_value}
                        random_item.update(new_error_filled_item)
                        original_field_name_item_list.append(random_item)

                    return {field_name: original_field_name_item_list}

        else:
            return {field_name: self.new_event_data[field_name]}

    def _create_key_errors(self):
        """Create errors in the ''keys'' of ``self.new_event_data['field_name']``
        according to the key error settings
        in ``self.config["schema"][field_name]['key_errors'] if key_error_mode
        is activated globally.

        Uses random float generation to implement simplistic probability of event errors.

        Operates directly on the ``self.new_event_data`` attribute so does not return.

        :param field_name: field_name to query both ``self.new_event_data`` and ``self.config["schema"]``

        """

        # check key error mode is active
        if self.config["error_mode"]["key_errors"]:
            if random.random() < self.config["error_mode"]["key_error_prob"]:
                key_list = list(self.new_event_data.keys())

                chosen_key = random.choice(key_list)
                # embracing randomness to either drop or mangle key

                if random.random() >= 0.5:
                    self.new_event_data.pop(chosen_key)
                else:
                    messed_up_key = chosen_key[: len(chosen_key) - 2]
                    self.new_event_data[messed_up_key] = self.new_event_data[chosen_key]
                    self.new_event_data.pop(chosen_key)
        else:
            pass

    def set_source_element(
        self, config_area=None, setting=None, new_setting_val=None, field_name=None
    ):
        """setter to change source config during server runtime"""
        if config_area == "schema":
            # print("sehcme")
            self.config[config_area][field_name].update({setting: new_setting_val})
        elif config_area in ["error_mode", "frequency"]:
            # print("error patch")
            self.config[config_area].update({setting: new_setting_val})

    @property
    def get_source_state(self):

        source_state = self.config

        return source_state
