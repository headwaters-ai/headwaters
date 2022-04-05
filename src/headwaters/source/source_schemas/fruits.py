"""early version of a schema config file for a source"""


data_file = "fruits_data.json"

schema = {
    "fruit": {
        "type": "choice",
        "default": ["tangerine", "tango", "turtles"],
        "existing": True,
    },
    "item": {
        "type": "increment",
        "default": 0,
        "existing": True,
    },
    "price": {
        "type": "increment",
        "default": 69.69,
        "existing": False,
    },
}
