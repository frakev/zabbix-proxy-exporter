# Zabbix Proxy Exporter

## Description
Zabbix Proxy Exporter reads into database Zabbix Proxy to retrieve informations.

:exclamation: It works only with SQLite database for now :exclamation:

## Prerequisites
You will need [Python 3.9+](https://www.python.org/) or later and prometheus-client==0.14.1

## Usage
````
python3 main.py --config=/etc/zabbix/zabbix_proxy.conf
````

## Output 
````
...
# HELP zbx_proxy_history Number of values in the proxy history table waiting to be sent to the server.
# TYPE zbx_proxy_history gauge
zbx_proxy_history{proxy="Zabbix Proxy"} 1123.0
# HELP zbx_proxy_hosts Number of monitored hosts.
# TYPE zbx_proxy_hosts gauge
zbx_proxy_hosts{proxy="Zabbix Proxy"} 16.0
# HELP zbx_items_value_type Number of items group by value_type.
# TYPE zbx_items_value_type gauge
zbx_items_value_type{proxy="Zabbix Proxy",value_type="0"} 284.0
zbx_items_value_type{proxy="Zabbix Proxy",value_type="1"} 2929.0
zbx_items_value_type{proxy="Zabbix Proxy",value_type="3"} 10305.0
zbx_items_value_type{proxy="Zabbix Proxy",value_type="4"} 92.0
# HELP zbx_enabled_items Number of enabled items.
# TYPE zbx_enabled_items gauge
zbx_enabled_items{proxy="Zabbix Proxy"} 12185.0
# HELP zbx_items_by_type Number of items by type.
# TYPE zbx_items_by_type gauge
zbx_items_by_type{proxy="Zabbix Proxy",type="3"} 41.0
zbx_items_by_type{proxy="Zabbix Proxy",type="4"} 12882.0
zbx_items_by_type{proxy="Zabbix Proxy",type="5"} 69.0
zbx_items_by_type{proxy="Zabbix Proxy",type="7"} 223.0
zbx_items_by_type{proxy="Zabbix Proxy",type="10"} 382.0
zbx_items_by_type{proxy="Zabbix Proxy",type="18"} 13.0
````


## :white_check_mark: TODO
- [x] Read Zabbix configuration file to connect to the database
- [ ] Get processes informations
and other things :)

## :star: Contributing
Feel free to contribute to the project by opening an issue if you find a bug or a pull request to add a feature.
