import pandas as pd
import random
import pkgutil
import json
import logging

# from .source_schemas import fruits


class Source:

    """
    This needs to be passed just a string indictaing the source type,
    and the instance needs to grab the data and schema from the right place
    using the pckg data...

    """

    def __init__(self, source_name):

        if not isinstance(source_name, str):
            raise ValueError(
                f"ValueError: 'source_name' parameter must be a string, passed type was {type(source_name)}"
            )

        supported_models = [
            "fruits",
        ]

        if source_name not in supported_models:
            raise ValueError(
                f"ValueError: passed 'source_name' of {source_name} is not supported"
            )

        self.name = source_name
        # self.created_data = []  # holding solution for the expanign choice issue

        self.get_schema()
        self.get_data()

    def get_schema(self):
        """use pkgutil to resolve and load the schema for the passed source_name

        expects a json config file at the mo'
        """
        try:
            initial_schema = pkgutil.get_data(
                "headwaters", f"/source/source_schemas/{self.name}.json"
            )
            print(initial_schema)
        except:
            raise

        initial_schema = json.loads(initial_schema)

        self.schema = initial_schema["schema"]
        self.data_file = initial_schema["data_file"]["path"]

    def get_data(self):
        """grab data from json file, simple

        right now, the data file is in a nice json dict shape, but pandas could be used to help with any data file
        in the futrue: csv, sql etc etc
        """

        initial_data = pkgutil.get_data(
            "headwaters", f"/source/source_data/{self.data_file}"
        )
        if self.data_file.endswith(".json"):
            self.initial_data = json.loads(initial_data)

        print(self.initial_data)

    def new_event(self):
        """create a new event based on instructions in the schema"""

        new_event = {}

        for k, v in self.schema.items():
            if v["type"] == "choice":
                if v['choice_from'] == "data_file":
                    # the update method maps all the keys of the data file to the new_event dict
                    # rather that nesting in a new_event[k] operation
                    new_event.update(random.choice(self.initial_data))

            if v["type"] == "random_int":
                new_event[k] = random.randint(v["rand_min"], v["rand_max"])


            # random_float, rnad_address, rand_name, rand_age, etc from faker

        return new_event
