import time
from influxdb import InfluxDBClient
from datetime import datetime
from zabbix import Zabbix
from variables import INFLUX_HOSTNAME, INFLUX_DATABASE


def get_triggers():
    """Get all triggers on Zabbix"""
    zabbix = Zabbix()
    all_triggers = list()
    for trigger in zabbix.triggered():
        all_triggers.append(trigger['description'])
    return all_triggers


def influx_send_metrics(metrics_hardware, metrics_ovpn):
    """Connecting to the influxDB"""
    client = InfluxDBClient(host=INFLUX_HOSTNAME, port=8086)
    client.create_database(INFLUX_DATABASE)
    client.switch_database(INFLUX_DATABASE)
    client.alter_retention_policy(name='autogen', duration='7d', database=INFLUX_DATABASE, default=False,
                                  shard_duration='7d')
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    add_metrics_hardware = [
        {
            'measurement': 'Trigger',
            'tags': {
                'Trigger': 'Системный блок - Down'
            },
            'time': current_time,
            'fields': {
                  "Metric": metrics_hardware
            }
        }
    ]
    add_metrics_ovpn = [
        {
            'measurement': 'Trigger',
            'tags': {
                'Trigger': 'Статус туннеля OVPN'
            },
            'time': current_time,
            'fields': {
                "Metric": metrics_ovpn
            }
        }
    ]
    try:
        client.write_points(add_metrics_hardware)
        print(f'Write metrics: {add_metrics_hardware}')
        client.write_points(add_metrics_ovpn)
        print(f'Write metrics: {add_metrics_ovpn}')
    except ConnectionError:
        time.sleep(300)
        pass


while True:
    counter_triggers_hardware = 0
    counter_triggers_ovpn = 0
    metric = get_triggers()
    for i in metric:
        if i == "Системный блок - Down (0)":
            counter_triggers_hardware += 1
        if i == "Статус туннеля VPN":
            counter_triggers_ovpn += 1
    influx_send_metrics(counter_triggers_hardware, counter_triggers_ovpn)
    time.sleep(5)
