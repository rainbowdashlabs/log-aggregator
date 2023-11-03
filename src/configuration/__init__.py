import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

from configuration.configuration import Configuration

_args: Namespace | None = None
_configuration: Configuration | None = None

import logging

log = logging.getLogger(__name__)

def args() -> Namespace:
    global _args
    if _args:
        return _args

    parser = ArgumentParser("log-aggregator")
    parser.add_argument('-c', '--config', default='./config/config.json')
    parser.add_argument('-l', '--logging', default='./config/logging.json')
    _args = parser.parse_args()
    return args()


def config() -> Configuration:
    global _configuration

    if _configuration:
        return _configuration

    path = Path(args().config)
    log.debug(f"Detected {path} for configuration file")
    _configuration = Configuration()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with path.open('r') as f:
            _configuration = Configuration(**json.loads(f.read()))

    with path.open('w') as f:
        f.write(_configuration.model_dump_json(indent=2))

    return config()
