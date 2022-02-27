""" expose model and data to domain class """

from .model import model
import json
import pkgutil

data = pkgutil.get_data(__package__, "data.json")
data = json.loads(data)
