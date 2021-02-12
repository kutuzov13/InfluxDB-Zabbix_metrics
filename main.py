import time
import viriables
from influxdb import InfluxDBClient
from datetime import datetime
from zabbix import Zabbix


def counter_triggers_ovpn():
    zabbix = Zabbix()
    all_triggers = list()
    for trigger in zabbix.triggered():
        all_triggers.append(trigger['description'])
    return all_triggers


def influx_send_metrics(metrics):
    """Connecting to the influxDB"""
    client = InfluxDBClient(host=viriables.INFLUX_HOSTNAME, port=8086)
    client.create_database(viriables.INFLUX_DATABASE)
    client.switch_database(viriables.INFLUX_DATABASE)
    client.alter_retention_policy(name='autogen', duration='7d', database=viriables.INFLUX_DATABASE, default=False,
                                  shard_duration='7d')
    current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    add_metrics = [
        {
            'measurement': 'Trigger',
            'tags': {
                'Trigger': 'Статус тунеля OVPN'
            },
            'time': current_time,
            'fields': {
                  "Metric": metrics
            }
        }
    ]
    try:
        print(f'Write metrics: {metrics}')
        client.write_points(add_metrics)
    except ConnectionError:
        time.sleep(300)
        pass


while True:
    counter_vpn = 0
    metric = counter_triggers_ovpn()
    for i in metric:
        if i == "Статус туннеля VPN":
            counter_vpn += 1
    influx_send_metrics(counter_vpn)
    time.sleep(5)
