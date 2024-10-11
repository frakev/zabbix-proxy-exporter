import logging
import sqlite3
import time
import socket
from prometheus_client import start_http_server, GaugeMetricFamily
from prometheus_client.core import REGISTRY
from optparse import OptionParser

# Logging configuration
logging.basicConfig(
    encoding="utf-8",
    level=logging.INFO,
    format="level=%(levelname)s datetime=%(asctime)s %(message)s",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Command-line arguments parsing
parser = OptionParser()
parser.add_option(
    "--config",
    dest="config_file",
    help="Path to the Zabbix Proxy configuration file (Default: /etc/zabbix/zabbix_proxy.conf).",
    default="/etc/zabbix/zabbix_proxy.conf",
)
parser.add_option("--port", dest="port", help="Listen port.", default=9200, type="int")
(options, domain) = parser.parse_args()
config_file = options.config_file
port = options.port

class ZabbixProxyExporter:
    def __init__(self):
        self.proxy = socket.gethostname()
        with open(config_file, "r") as conf_proxy:
            for line in conf_proxy:
                if "DBName" in line:
                    line = line.strip()
                    self.db = line[7:]
                if "Hostname" in line and "#" not in line:
                    line = line.strip()
                    self.proxy = line[9:]
        self.con = None  # Initialize database connection

    def __open_database(self):
        try:
            logging.info("Initializing database")
            self.con = sqlite3.connect(self.db, check_same_thread=False)
            self.cur = self.con.cursor()
        except sqlite3.Error as e:
            logging.error(f"Error opening database: {e}")
            raise  # Re-raise the exception to stop execution

    def __close_db(self):
        if self.con:
            logging.info("Closing database")
            self.con.close()

    def get_value_type_items(self):
        logger.info("Get number of items by value_type")
        try:
            res = self.cur.execute(
                "select value_type, count(*) from items group by value_type;"
            )
            return res.fetchall()  # Return query results
        except sqlite3.Error as e:
            logging.error(f"Error executing query: {e}")
            return []  # Return an empty list in case of error

    def set_value_type_items(self, data):
        metric = GaugeMetricFamily(
            "zbx_items_value_type",
            "Number of items grouped by value_type.",
            labels=["value_type", "proxy"],
        )
        for d in data:
            metric.add_metric([str(d[0]), self.proxy], d[1])
        return metric

    def get_proxy_queue(self):
        logger.info("Get proxy queue information")
        try:
            res = self.cur.execute(
                "select max(id)-(select nextid from ids where table_name = 'proxy_history' limit 1) from proxy_history;"
            )
            return res.fetchone()  # Return query result
        except sqlite3.Error as e:
            logging.error(f"Error executing query: {e}")
            return (None,)  # Return an empty tuple in case of error

    def set_proxy_queue(self, data):
        metric = GaugeMetricFamily(
            "zbx_proxy_history",
            "Number of values in the proxy history table waiting to be sent to the server.",
            labels=["proxy"],
        )
        if data[0] is not None:  # Check if value is None
            metric.add_metric([self.proxy], data[0])
        return metric

    def get_proxy_hosts(self):
        logger.info("Get proxy hosts information")
        try:
            res = self.cur.execute("select count(*) from hosts where status = 0;")
            return res.fetchone()  # Return query result
        except sqlite3.Error as e:
            logging.error(f"Error executing query: {e}")
            return (None,)  # Return an empty tuple in case of error

    def set_proxy_hosts(self, data):
        metric = GaugeMetricFamily(
            "zbx_proxy_hosts", "Number of monitored hosts.", labels=["proxy"]
        )
        if data[0] is not None:  # Check if value is None
            metric.add_metric([self.proxy], data[0])
        return metric

    def get_number_enabled_items(self):
        logger.info("Get number of enabled items")
        try:
            res = self.cur.execute("select count(*) from items where status = 0;")
            return res.fetchone()  # Return query result
        except sqlite3.Error as e:
            logging.error(f"Error executing query: {e}")
            return (None,)  # Return an empty tuple in case of error

    def set_number_enabled_items(self, data):
        metric = GaugeMetricFamily(
            "zbx_enabled_items", "Number of enabled items.", labels=["proxy"]
        )
        if data[0] is not None:  # Check if value is None
            metric.add_metric([self.proxy], data[0])
        return metric

    def get_items_type(self):
        logger.info("Get number of enabled items by type")
        try:
            res = self.cur.execute("select type, count(*) from items group by type")
            return res.fetchall()  # Return query results
        except sqlite3.Error as e:
            logging.error(f"Error executing query: {e}")
            return []  # Return an empty list in case of error

    def set_items_type(self, data):
        metric = GaugeMetricFamily(
            "zbx_items_by_type", "Number of items by type.", labels=["type", "proxy"]
        )
        for d in data:
            metric.add_metric([str(d[0]), self.proxy], d[1])
        return metric

    def collect(self):
        try:
            self.__open_database()  # Open connection once at the beginning
            logger.info("Collecting proxy information")
            data = self.get_proxy_queue()
            yield self.set_proxy_queue(data)
            data = self.get_proxy_hosts()
            yield self.set_proxy_hosts(data)
            data = self.get_value_type_items()
            yield self.set_value_type_items(data)
            data = self.get_number_enabled_items()
            yield self.set_number_enabled_items(data)
            data = self.get_items_type()
            yield self.set_items_type(data)
            logger.info("Done collecting proxy information")
        except Exception as e:
            logging.error(f"An error occurred during collection: {e}")
        finally:
            self.__close_db()  # Ensure connection is closed in case of errors

if __name__ == "__main__":
    collector = ZabbixProxyExporter()

    start_http_server(port)

    REGISTRY.register(collector)

    while True:
        time.sleep(30)
