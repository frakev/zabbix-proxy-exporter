import logging
import sqlite3
import time
from prometheus_client import start_http_server, Summary, Gauge
from prometheus_client.metrics_core import (
    GaugeMetricFamily,
    HistogramMetricFamily,
    GaugeHistogramMetricFamily,
)
from prometheus_client.core import REGISTRY
from prometheus_client.utils import INF

format_string = "level=%(levelname)s datetime=%(asctime)s %(message)s"
logging.basicConfig(encoding="utf-8", level=logging.INFO, format=format_string)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ZabbixProxyExporter():
	con = sqlite3.connect("zabbix_proxy.db", check_same_thread=False)
	cur = con.cursor()

	def get_proxy_queue(self):
		logger.info("Get proxy queue informations")
		res = self.cur.execute('select max(id)-(select nextid from ids where table_name = "proxy_history" limit 1) from proxy_history;')
		return res

	def set_proxy_queue(self, proxy_queue):
		zabbix_proxy_queue = GaugeMetricFamily(
			"zabbix_proxy_queue", "Data in queue to send", labels=[]
		)
		for queue in proxy_queue:
			zabbix_proxy_queue.add_metric("", queue[0])
		return zabbix_proxy_queue

	def get_proxy_hosts(self):
		logger.info("Get proxy hosts informations")
		res = self.cur.execute('select count(*) from hosts where status = 0;')
		return res

	def set_proxy_hosts(self, proxy_hosts):
		zabbix_proxy_hosts = GaugeMetricFamily(
			"zabbix_proxy_hosts", "Number of hosts", labels=[]
		)
		for nb in proxy_hosts:
			zabbix_proxy_hosts.add_metric("", nb[0])
		return zabbix_proxy_hosts

	def collect(self):
		logger.info("Collect proxy stats")
		proxy_queue = self.get_proxy_queue()
		yield self.set_proxy_queue(proxy_queue)
		proxy_hosts = self.get_proxy_hosts()
		yield self.set_proxy_hosts(proxy_hosts)
		logger.info("Done proxy stats")

	#con.close()



if __name__ == "__main__":
	collector = ZabbixProxyExporter()

	start_http_server(9200)

	REGISTRY.register(collector)

	while True:
		time.sleep(30)

