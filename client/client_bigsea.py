import ConfigParser
import json
import os
import requests
import sys


config = ConfigParser.RawConfigParser()
__file__ = os.path.join(sys.path[0], 'client_bigsea.cfg')
config.read(__file__)


plugin = config.get('manager', 'plugin')
cluster_size = config.getint('manager', 'cluster_size')
flavor_id = config.get('manager', 'flavor_id')
image_id = config.get('manager', 'image_id')

command = config.get('plugin', 'command')
reference_value = config.getfloat('plugin', 'reference_value')
log_path = config.get('plugin', 'log_path')


scaler_plugin = config.get('scaler', 'scaler_plugin')
actuator = config.get('scaler', 'actuator')
metric_source = config.get('scaler', 'metric_source')
check_interval = config.getint('scaler', 'check_interval')
trigger_down = config.getint('scaler', 'trigger_down')
trigger_up = config.getint('scaler', 'trigger_up')
min_cap = config.getint('scaler', 'min_cap')
max_cap = config.getint('scaler', 'max_cap')
actuation_size = config.getint('scaler', 'actuation_size')
metric_rounding = config.getint('scaler', 'metric_rounding')


headers = {'Content-Type': 'application/json'}
body = dict(plugin=plugin, scaler_plugin=scaler_plugin,
	actuator=actuator, metric_source=metric_source, check_interval=check_interval,
	trigger_down=trigger_down, trigger_up=trigger_up,
	min_cap=min_cap, max_cap=max_cap, actuation_size=actuation_size,
        metric_rounding=metric_rounding, cluster_size=cluster_size,
	flavor_id=flavor_id, image_id=image_id, command=command,
        reference_value=reference_value,
        log_path=log_path
        )
url = "<manager_service_ip:port>"
print "Making request to", url
body_log = body.copy()
print "Passing arguments as", body_log
r = requests.post(url, headers=headers, data=json.dumps(body))
print r.content
print r.text
