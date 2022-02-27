from marshmallow import fields
import random

model = {
    "fruit": {
        "field": fields.String(required=True),
        "stream": {
            "type": "choice",
            "default": 'tangerine',
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
        "field": fields.Float(missing=random.randint(2, 200)),
        "stream": {
            "type": "infer",
            "default": 69.69,
            "include": True,
            "existing": False,
        },
    },
}