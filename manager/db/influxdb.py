from typing import List
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import WritePrecision, InfluxDBClient, Point
from datetime import datetime


class DataUsageDB:
    def __init__(self, url, token, org) -> None:
        self.url = url
        self.token = token
        self.org = org
        self.bucket = "usage"
        self.__client = None

    @property
    def client(self) -> InfluxDBClient:
        if self.__client is None:
            self.__client = InfluxDBClient(url=self.url, token=self.token, org=self.org)

        return self.__client

    @staticmethod
    def create_point(
        measurement: str,
        tags: dict,
        fields: dict,
        time=None,
        write_precision: WritePrecision = WritePrecision.MS,
    ):
        if not isinstance(measurement, str):
            raise TypeError("measurement must be str")
        if not isinstance(tags, dict):
            raise TypeError("tags must be dict")
        if not isinstance(fields, dict):
            raise TypeError("fields must be dict")
        if not time:
            time = datetime.utcnow()

        point_dict = {}

        point_dict["measurement"] = measurement
        point_dict["tags"] = tags
        point_dict["fields"] = fields
        point_dict["time"] = time

        return Point.from_dict(point_dict, write_precision=write_precision)

    def write(self, key_id, usage, org=None):
        p = (
            Point("data_usage")
            .tag("key_id", key_id)
            .field("usage", usage)
            .time(datetime.utcnow(), WritePrecision.MS)
        )

        with self.client.write_api(write_options=SYNCHRONOUS) as write_api:
            write_api.write(bucket=self.bucket, org=org, record=p)

    def read(self, logger=None):
        if not logger:
            logger = print
        else:
            logger = logger.info

        query_api = self.client.query_api()

        tables = query_api.query(f'from(bucket: "{self.bucket}") |> range(start: -30d)')

        for table in tables:
            for record in table.records:
                logger(
                    str(record["_time"])
                    + " - "
                    + record.get_measurement()
                    + " "
                    + record.get_field()
                    + "="
                    + str(record.get_value())
                )
