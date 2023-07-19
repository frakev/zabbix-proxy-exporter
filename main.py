import logging
import sqlite3
import time
import socket
from prometheus_client import start_http_server, Summary, Gauge
from prometheus_client.metrics_core import (
    GaugeMetricFamily,
    HistogramMetricFamily,
    GaugeHistogramMetricFamily,
)
from prometheus_client.core import REGISTRY
from prometheus_client.utils import INF
from optparse import OptionParser

parser = OptionParser()

format_string = "level=%(levelname)s datetime=%(asctime)s %(message)s"
logging.basicConfig(encoding="utf-8", level=logging.INFO, format=format_string)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

parser.add_option("--config", dest="config_file", help="Path to the Zabbix Proxy configuration file (Default: /etc/zabbix/zabbix_proxy.conf).", default="/etc/zabbix/zabbix_proxy.conf")

(options, domain) = parser.parse_args()
config_file = options.config_file

class ZabbixProxyExporter():

	def __init__(self):
		self.proxy = socket.gethostname()
		with open(config_file,"r") as conf_proxy:
			for num, line in enumerate(conf_proxy, 1):
				if 'DBName' in line:
					line = line.strip()
					self.db = line[7:]
				if 'Hostname' in line and "#" not in line:
					line = line.strip()
					self.proxy = line[9:]

	def open_database(self):
		logging.info("Initialize database")
		self.con = sqlite3.connect(self.db, check_same_thread=False)
		self.cur = self.con.cursor()

	def get_value_type_items(self):
		logger.info("Get number of items by value_type")
		res = self.cur.execute("select value_type, count(*) from items group by value_type;")
		return res

	def set_value_type_items(self, data):
		metric = GaugeMetricFamily(
			"zbx_items_value_type", "Number of items group by value_type.", labels=["value_type", "proxy"]
		)
		for d in data:
			metric.add_metric([str(d[0]), self.proxy], d[1])
		return metric

	def get_proxy_queue(self):
		logger.info("Get proxy queue informations")
		res = self.cur.execute('select max(id)-(select nextid from ids where table_name = "proxy_history" limit 1) from proxy_history;')
		return res

	def set_proxy_queue(self, data):
		metric = GaugeMetricFamily(
			"zbx_proxy_history", "Number of values in the proxy history table waiting to be sent to the server.", labels=["proxy"]
		)
		for d in data:
			metric.add_metric([self.proxy], d[0])
		return metric

	def get_proxy_hosts(self):
		logger.info("Get proxy hosts informations")
		res = self.cur.execute('select count(*) from hosts where status = 0;')
		return res

	def set_proxy_hosts(self, data):
		metric = GaugeMetricFamily(
			"zbx_proxy_hosts", "Number of monitored hosts.", labels=["proxy"]
		)
		for d in data:
			metric.add_metric([self.proxy], d[0])
		return metric

	def get_number_enabled_items(self):
		logger.info("Get number of enabled items")
		res = self.cur.execute('select count(*) from items where status = 0;')
		return res

	def set_number_enabled_items(self, data):
		metric = GaugeMetricFamily(
			"zbx_enabled_items", "Number of enabled items.", labels=["proxy"]
		)
		for d in data:
			metric.add_metric([self.proxy], d[0])
		return metric

	def close_db(self):
		logging.info("Database closed")
		self.con.close()

	def collect(self):
		
		self.open_database()
		logger.info("Collect proxy informations")
		data = self.get_proxy_queue()
		yield self.set_proxy_queue(data)
		data = self.get_proxy_hosts()
		yield self.set_proxy_hosts(data)
		data = self.get_value_type_items()
		yield self.set_value_type_items(data)
		data = self.get_number_enabled_items()
		yield self.set_number_enabled_items(data)
		logger.info("Done proxy informations")
		self.close_db()
	

if __name__ == "__main__":
	collector = ZabbixProxyExporter()

	start_http_server(9200)

	REGISTRY.register(collector)

	while True:
		time.sleep(30)
