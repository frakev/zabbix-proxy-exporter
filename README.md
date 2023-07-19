# Zabbix Proxy Exporter

## Description
Zabbix Proxy Exporter reads into database Zabbix Proxy to retrieve informations.

## Prerequisites
You will need [Python 3.6+](https://www.python.org/) or later and prometheus-client==0.14.1

## Usage
````
> python3 main.py --config=/etc/zabbix/zabbix_proxy.conf
```

## TODO
- Read Zabbix configuration file to connect to the database
- Retrieve number of items
- Get processes informations
and other things :)
