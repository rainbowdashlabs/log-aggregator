import datetime
from urllib.parse import quote_plus

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel


class Mongo(BaseModel):
    user: str = 'root'
    password: str = 'example'
    host: str = 'localhost'
    port: int = 27017
    database: str = 'log-aggregator'

    def uri(self):
        return f"mongodb://{quote_plus(self.user)}:{quote_plus(self.password)}@{self.host}:{self.port}"


class Socket(BaseModel):
    host: str = '0.0.0.0'
    port: int = 8888


class Format(BaseModel):
    required_keys: list[str] = []
    # this is a required key as well but the value has to be one of the listed values
    restricted_values: dict[str, list[str]] = {'index': ["example"]}

    def validate(self, log: dict):
        missing = [i for i in self.required_keys if i not in log]
        if missing:
            # avoids circular import
            from connection.exceptions import ValidationException
            raise ValidationException(f"Missing key/s {missing}")


class Retention(BaseModel):
    active: bool = False
    years: int = 0
    months: int = 0
    days: int = 30
    hours: int = 0
    seconds: int = 0

    def timestamp(self) -> datetime.datetime:
        now = datetime.datetime.now(datetime.UTC)
        delta = relativedelta(years=self.years,
                              months=self.months,
                              days=self.days,
                              hours=self.hours,
                              seconds=self.seconds)
        return now - delta


class Index(BaseModel):
    retention: Retention = Retention()
    format: Format = Format(required_keys=[], restricted_values={})


class Indices(BaseModel):
    block_unkown: bool = False
    index_field: str = 'index'
    indices: dict[str, Index] = {'example': Index()}

    def __index__(self):
        return self.indices


class Storage(BaseModel):
    retention: Retention = Retention()


class Configuration(BaseModel):
    mongo: Mongo = Mongo()
    socket: Socket = Socket()
    format: Format = Format()
    retention: Retention = Retention()
    indices: Indices = Indices()
