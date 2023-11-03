import json
import logging
import socket

from configuration import config
from connection.exceptions import ValidationException
from data import add_log

log = logging.getLogger(__name__)


def _validate(log: dict):
    i_format = config().format
    if config().indices.block_unkown:
        if 'index' not in log:
            raise ValidationException('Index is missing in payload')
        if 'index' not in config().indices:
            raise ValidationException(f'Index {log['index']} is unkown')

    if 'index' in log and log['index'] in config().indices:
        i_format = config().indices[log['indices']]

    i_format.format.validate(log)


def start():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config().socket.host, config().socket.port))

    try:
        while True:
            _read(sock)
    except Exception as e:
        log.error(f"error", e)


def _read(sock):
    while True:
        log.debug("waiting to receive message")
        data, addr = sock.recvfrom(1024 * 1024 * 4)

        payload = data.decode('utf-8')
        try:
            record = json.loads(payload)
            _validate(record)
            log.debug(f"Received json message: {record}")
            add_log(record)
        except json.JSONDecodeError:
            log.warning(f"received non-json message: {payload}")
        except ValidationException as e:
            log.warning(e.msg)
            log.warning(payload.strip())
