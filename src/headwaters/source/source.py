import pandas as pd
import random
import pkgutil
import json
import logging

from .source_schemas import fruits


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

        if self.name == "fruits":
            self.schema = fruits.schema
            self.data_file = fruits.data_file

        self.created_data = []  # holding solution for the expanign choice issue

        self.load_data()

    def load_data(self):
        """use pandas as core data wrangler mediator type thing.

        right now, the data file is in a nice json dict shape, but pandas is here to help with any data file
        in the futrue: csv, sql etc etc


        """

        # this key list section finds the keys from the model that are expected to be in the
        # data_file for this source and that the schema WANTS TO STREAM
        # if the key/field is present in the data_file but not in the key_list, it won't make it to pandas
        # and so won't be streamed
        key_list = []

        for k in self.schema.keys():
            if self.schema[k]["existing"]:
                key_list.append(k)

        initial_data = pkgutil.get_data(
            "headwaters", f"/source/source_data/{self.data_file}"
        )
        if self.data_file.endswith(".json"):
            initial_data = json.loads(initial_data)

        print(initial_data)

        df = pd.DataFrame(data=initial_data, columns=key_list)
        print(df)

        self.initial_data = df.to_dict(orient="records")

    def new_event(self):
        """create a new event based on instructions in the schema"""

        new_event = {}

        for k in self.schema.keys():

            field = self.schema[k]
            default = self.schema[k]["default"]

            # this is a random choice from the inital_data
            if field["type"] == "choice":
                try:
                    new_event[k] = random.choice(self.initial_data)[k]
                except KeyError:
                    """handles where an event field not in the original data is being picked from"""
                    new_event[k] = random.choice(default)

            if field["type"] == "increment":
                try:
                    new_event[k] = self.created_data[-1][k] + 1
                except:
                    new_event[k] = default

        self.created_data.append(new_event)
        return new_event
