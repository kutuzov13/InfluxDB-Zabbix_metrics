import os
import time
from datetime import datetime

from influxdb.exceptions import InfluxDBClientError
from influxdb import InfluxDBClient
from zabbix import Zabbix

INFLUXDB_HOST = os.getenv('INFLUXDB_HOST')
INFLUXDB_DATABASE = os.getenv('INFLUXDB_DATABASE')
INFLUXDB_PORT = 8086


def get_triggers():
    """Get all triggers on Zabbix."""
    zabbix = Zabbix()
    all_triggers = list()
    for trigger in zabbix.triggered():
        all_triggers.append(trigger['description'])
    return all_triggers


def influx_send_metrics(metrics_name, metrics_value):
    """Connecting to the influxDB."""
    client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
    try:
        client.create_database(INFLUXDB_DATABASE)
        client.alter_retention_policy(
            name='autogen',
            duration='7d',
            database=INFLUXDB_DATABASE,
            default=False,
            shard_duration='7d'
        )
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        add_metrics_hardware = [
            {
                'measurement': f'{metrics_name}',
                'tags': {
                    'Name': metrics_name,
                },
                'time': current_time,
                'fields': {
                    "Value": metrics_value,
                },
            },
        ]
        client.write_points(add_metrics_hardware)
        
    except InfluxDBClientError:
    client.create_database(INFLUXDB_DB)
    client.close()
