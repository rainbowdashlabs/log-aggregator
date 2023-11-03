# Log Aggregator

A very simple log aggregator that dumps json strings received via udp into a MongoDB.

Has several configurations options like global log retention, field validation and also supports indices with specific settings.

## Configuration

### Mongo

Log Aggregator requires a mongoDB to work.
Set your credentials and stuff in the mongo section.

```json
{
  "mongo": {
    "user": "root",
    "password": "example",
    "host": "mongodb",
    "port": 27017,
    "database": "log-aggregator"
  }
}
```

### Socket

The socket is defined here. You can set the host and port.

```json
{
  "socket": {
    "host": "0.0.0.0",
    "port": 8888
  }
}
```

### Format

The format section allows to set format requirements for the incoming json objects.

```json
{
  "format": {
    "required_keys": [],
    "restricted_values": {
      "index": [
        "example"
      ]
    }
  }
}
```

#### Required keys

Required keys is an array of keys that are expected at the toplevel of the json object.

#### Restricted Values

Restricted values is a dictionary which contains a list of valid values for each key.

### Retention

Retention modifies the time after which a log is deleted. Retention is optional and turned off by default.

```json
{
  "retention": {
    "active": false,
    "years": 0,
    "months": 0,
    "days": 30,
    "hours": 0,
    "seconds": 0
  }
}
```

### Indices

Indices allows to enforce retention and formating rules on a per index level.

```json
{
  "indices": {
    "block_unkown": false,
    "index_field": "_index",
    "indices": {
      "example": {
        "retention": {
          "active": false,
          "years": 0,
          "months": 0,
          "days": 30,
          "hours": 0,
          "seconds": 0
        },
        "format": {
          "required_keys": [],
          "restricted_values": {}
        }
      }
    }
  }
}
```

Indices are identified by value of the `_index` field at the toplevel of the object.
The field can be changed by changing `index_field`.
**Please be aware that changing that value afterward will break the application**

The `block_unkown` will block every record that is missing the index field or is not registered under indices.

The `indices` section contains a dict which an entry for each index with retention and format settings.

If an index is registered here, global rules for retention and format do no longer apply.
