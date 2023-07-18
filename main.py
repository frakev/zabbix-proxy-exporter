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

	def __init__(self):
		with open("/etc/zabbix/zabbix_proxy.conf","r") as conf_proxy:
			for num, line in enumerate(conf_proxy, 1):
				if 'DBName' in line:
					line = line.strip()
					self.db = line[7:]

	def open_database(self):
		logging.info("Initialize database")
		self.con = sqlite3.connect(self.db, check_same_thread=False)
		self.cur = self.con.cursor()

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

	def close_db(self):
		logging.info("Database closed")
		self.con.close()

	def collect(self):

		self.open_database()
		logger.info("Collect proxy stats")
		proxy_queue = self.get_proxy_queue()
		yield self.set_proxy_queue(proxy_queue)
		proxy_hosts = self.get_proxy_hosts()
		yield self.set_proxy_hosts(proxy_hosts)
		logger.info("Done proxy stats")
		self.close_db()


if __name__ == "__main__":
	collector = ZabbixProxyExporter()

	start_http_server(9200)

	REGISTRY.register(collector)

	while True:
		time.sleep(30)
