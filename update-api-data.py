"""Regenerates the method list"""

import json
import os

import requests


def sorted_dict(data: dict) -> dict:
    return {
        k: (sorted_dict(data[k]) if isinstance(data[k], dict) else data[k])
        for k in sorted(data.keys())
    }


res = requests.get('http://api.ipernity.com/api/api.methods.getList/json')

methods = sorted(
    res.json()['methods']['method'],
    key = lambda x: x['name']
)

destfile = os.path.join(
    os.path.dirname(__file__),
    'ipernity',
    'methods.json'
)

methods2 = {
    m['name']: sorted_dict(m)
    for m in methods
}

with open(destfile, 'w') as df:
    json.dump(methods2, df, indent = 4)



