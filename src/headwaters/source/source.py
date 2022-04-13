import random
import pkgutil
import json
from json.decoder import JSONDecodeError
import uuid
from datetime import datetime


class Source:

    """
    The Source class provides the mechanism to create a ``new_event`` from existing
    data, freshly created data, or a combination of both. Class attribute dictionaries
    of ``self.schema``, ``self.errors`` and ``self.existing`` are loaded from a
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

        supported_schemas = [
            "fruit_sales",
        ]

        if source_name not in supported_schemas:
            raise ValueError(
                f"ValueError: passed 'source_name' of {source_name} is not supported"
            )

        # attributes
        self.name = source_name
        self.errors = {}  # will be populated by self._load_schema method call
        self.schema = {}  # will be populated by self._load_schema method call
        self.existing_data = {}  # will be populated by self._load_schema method call
        self.new_event_data = {}  # will be used by the self.new_event method

        # once checks pass, go and grab the relevant data
        self._load_schema()

    def _load_schema(self) -> None:
        """use pkgutil to resolve and load the schema for the passed source_name

        expects a json config file.
        """

        try:
            initial_schema = pkgutil.get_data(
                "headwaters", f"/source/schemas/{self.name}.json"
            )
        except:
            # just bubbling the error up right now, this will need to change
            raise

        try:
            initial_schema = json.loads(initial_schema)
        except JSONDecodeError:
            raise ValueError(
                f"error parsing json config file for {self.name}, is there an error in the {self.name}.json file?"
            )

        self.schema = initial_schema["schema"]
        self.errors = initial_schema["errors"]
        self.existing_data = initial_schema["data"]

    def new_event(self) -> dict:
        """Create and return a ``new_event`` dictionary object according to the
        settings in attributes ``self.schema`` and ``self.errors``

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

        return self.new_event_data

    def _select_existing(self, field_name: str) -> dict:

        """Given the field_name to search the schema for,
        check the 'select_method' and
        'select_quantity' of the schema for that ``field_name`` and return a
         dict keyed by field_name with value of
        a list of selected dict items from ``self.existing_data``.

        :param field_name: 'field_name' is the key of the
        ``self.schema`` dictionary like this: ``self.schema[field_name]``

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
                    # this assumes that the value of each ``field_name`` in
                    # existing data is a list. This assumption may not always hold?
                    output_values.append(random.choice(self.existing_data[field_name]))

            # in the case of the 'many' string:
            if field_settings["select_quantity"] == "many":
                # we need to know the length of the data, then can use that
                # as the max for a randint to use as the range:
                range_max = len(self.existing_data[field_name])

                for _ in range(random.randint(1, range_max)):
                    output_values.append(random.choice(self.existing_data[field_name]))

        return_shape = {field_name: output_values}

        return return_shape

    def _create_new(self, field_name: str) -> dict:
        """Create a new value for a supplied field_name (ie the top_level key of
        ``self.schema``) and return a dict of a list of dicts keyed by ``field_name``:

        The quantity of items generated and appended to  the list is
        controlled by the ``create_volume`` setting.

        :param field_name: the ``field_name`` is the key of the
        ``self.schema`` dictionary ``self.schema[field_name]``

        :returns: dict keyed by ``field_name`` with value set as a
        list of dicts of generated new items of shape:

        ..code-block:: python

            {
                'field_name': [
                    {field_name: new_value},
                ]
            }

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
        """Filter the data selected from existing data
        returns a dict of a list of dicts keyed by ``field_name``:

        :param field_name: the ``field_name`` is the key of the
        ``self.schema`` dictionary ``self.schema[field_name]``

        :returns: dict keyed by ``field_name`` with value set as a list of dicts
        of generated new items of shape:

        ..code-block:: python

            {
                'field_name': [
                    {field_name: new_value},
                ]
            }
        """

        settings = self.schema[field_name]

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

        :param field_name: the field_name of both ``self.schema`` and ``self.new_event_data``

        """

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
        """Flatten values of provided field_name key to the top level
        of the ``self.new_event_data`` dictionary.



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

    def _create_value_errors(self, field_name: str) -> None:
        """Create errors in the ''values'' of ``self.new_event_data['field_name']``
        according to the value error settings
        in ``self.schema[field_name]['value_errors'] if value_error_mode
        is activated globally.

        Uses random float generation to implement simplistic probability of event errors.

        Operates directly on the ``self.new_event_data`` attribute so does not return.

        :param field_name: field_name to query both ``self.new_event_data`` and ``self.schema``

        """

        # ``self.errors`` specifies the active error mode as includign value_errors
        if self.errors["value_errors"]:
            if random.random() < self.errors["value_error_prob"]:
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
        """Create errors in the ''keys'' of ``self.new_event_data['field_name']``
        according to the key error settings
        in ``self.schema[field_name]['key_errors'] if key_error_mode
        is activated globally.

        Uses random float generation to implement simplistic probability of event errors.

        Operates directly on the ``self.new_event_data`` attribute so does not return.

        :param field_name: field_name to query both ``self.new_event_data`` and ``self.schema``

        """

        # check key error mode is active
        if self.errors["key_errors"]:
            if random.random() < self.errors["key_error_prob"]:
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

    def set_schema(self, field_name, new_val):
        """ test setter to change flatten during server runtime """

        # check new_val is a bool

        if isinstance(new_val, bool):
            self.schema[field_name]['flatten'] = new_val

    @property
    def source_status(self):
        pass