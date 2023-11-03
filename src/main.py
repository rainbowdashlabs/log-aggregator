import json
from logging import config as log_conf
from pathlib import Path

from configuration import args, config
import connection

import logging

log = logging.getLogger(__name__)

if __name__ == '__main__':
    conf_file = Path(args().logging)
    with conf_file.open('r') as f:
        log_conf.dictConfig(json.load(f))
        log.debug(f"Detected {conf_file} as logging configuration")
    config()
    connection.start()
