# Zabbix Proxy Exporter

## Description
Zabbix Proxy Exporter reads into database Zabbix Proxy to retrieve informations.

:exclamation: It works only with SQLite database for now :exclamation:

## Prerequisites
You will need [Python 3.6+](https://www.python.org/) or later and prometheus-client==0.14.1

## Usage
````
python3 main.py --config=/etc/zabbix/zabbix_proxy.conf
````

## TODO
- [x] Read Zabbix configuration file to connect to the database
- [ ] Get processes informations
and other things :)
