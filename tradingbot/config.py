import json
from typing import Dict


def get_config() -> Dict:
    with open('./config.json') as conf:
        data = json.load(conf)

    return data
