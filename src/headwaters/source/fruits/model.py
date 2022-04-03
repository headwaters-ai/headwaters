from marshmallow import fields
import random

data = [
    {"fruit": "apple", "item": 1},
    {"fruit": "banana", "item": 2},
    {"fruit": "cherry", "item": 3},
    {"fruit": "damson", "item": 4},
    {"fruit": "elderberry", "item": 5}
]

model = {
    "fruit": {
        "field": fields.String(required=True),
        "stream": {
            "type": "choice",
            "default": ['tangerine', 'tango', 'turtles'],
            "include": True,
            "existing": True,
        },
    },
    "item": {
        "field": fields.Integer(required=True),
        "stream": {
            "type": "increment",
            "default": 0,
            "include": True,
            "existing": True,
        },
    },
    "price": {
        # "field": fields.Float(missing=random.randint(2, 200)),
        "stream": {
            "type": "increment",
            "default": 69.69,
            "include": True,
            "existing": False,
        },
    },
}