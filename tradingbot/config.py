import json
from typing import Any, Dict


def get_config() -> Dict[str, Any]:
    with open("./config.json") as conf:
        data = json.load(conf)

    return data
