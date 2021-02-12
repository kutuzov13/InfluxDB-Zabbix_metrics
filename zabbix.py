import viriables
from pyzabbix.api import ZabbixAPI


class Zabbix:
    def __init__(self):
        self.zabbix = ZabbixAPI(url=viriables.URL, user=viriables.USER, password=viriables.PASSWORD)

    def triggered(self):
        result = self.zabbix.trigger.get(only_true=1,
                                         skipDependent=1,
                                         monitored=1,
                                         active=1,
                                         output='extend',
                                         expandDescription=1)
        return result
