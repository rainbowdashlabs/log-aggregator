import json
import logging
import socket

from configuration import config
from connection.exceptions import ValidationException
from data import add_log

log = logging.getLogger(__name__)


def _validate(record: dict) -> dict:
    i_format = config().format
    if config().indices.block_unkown:
        if 'index' not in record:
            raise ValidationException('Index is missing in payload')
        if 'index' not in config().indices:
            raise ValidationException(f'Index {record['index']} is unkown')

    if 'index' in record and record['index'] in config().indices:
        i_format = config().indices[record['indices']]

    i_format.validate(record)
    if i_format.harmonize_keys:
        return _transform(record)
    return record


def start():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((config().socket.host, config().socket.port))

    try:
        while True:
            _read(sock)
    except Exception as e:
        log.error(f"error", e)


def _transform(record: dict):
    result = {}

    for k, v in record.items():
        result = deep_merge(result, _split(k, v))

    return result


def _split(key, value) -> dict:
    if "." not in key:
        return {key: value}
    split = str.split(key, ".", 1)
    return {split[0]: _split(split[1], value)}


def deep_merge(dict1, dict2):
    result = dict1.copy()
    for k, v in dict2.items():
        if isinstance(v, dict) and k in dict1 and isinstance(dict1[k], dict):
            result[k] = deep_merge(dict1[k], v)
        else:
            result[k] = v
    return result


def _read(sock):
    while True:
        log.debug("waiting to receive message")
        data, addr = sock.recvfrom(1024 * 1024 * 4)

        print(addr)

        payload = data.decode('utf-8')
        try:
            record = json.loads(payload)
            record['_ip'] = {"host": addr[0], "port": str(addr[1])}
            _validate(record)
            log.debug(f"Received json message: {record}")
            add_log(record)
        except json.JSONDecodeError:
            log.warning(f"received non-json message: {payload}")
        except ValidationException as e:
            log.warning(e.msg)
            log.warning(payload.strip())


if __name__ == '__main__':
    print(_transform({"log.level.another": "INFO"}))
