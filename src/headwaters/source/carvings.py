""" holding area fro code carved out of mainline code, coudl be useful int he future"""

def create_data_schema(self):
    """create a marshmallow schema from passed model looking for data def only
    only therefore applies to data that exists in the data files, so can exlude
    existing: False

    """
    d = {}
    for k in self.model.keys():
        if self.model[k]["stream"]["existing"]:
            d.update({k: self.model[k]["field"]})

    DataSchema = Schema.from_dict(d)
    return DataSchema

def validate_data(self):
    """
    use create marshmallow instance to validate passed data
    """

    DataSchema = self.create_data_schema()

    try:

        DataSchema(many=True).load(self.data)
        return True
    except ValidationError as e:
        logging.info(e)
        return False

def set_field(self, data):
    """setter to add a new field to running source instance"""
    new_field = data["new_field"]
    self.model[new_field] = data["settings"]

    return "set_field complete"