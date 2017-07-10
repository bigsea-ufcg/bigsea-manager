import ConfigParser
import json
import os
import requests
import sys


config = ConfigParser.RawConfigParser()
__file__ = os.path.join(sys.path[0], 'os_generic.cfg')
config.read(__file__)


manager_ip = config.get('manager', 'ip')
manager_port = config.get('manager', 'port')
plugin = config.get('manager', 'plugin')
scaler_plugin = config.get('manager', 'scaler_plugin')

cluster_size = config.getint('plugin', 'cluster_size')
flavor_id = config.get('plugin', 'flavor_id')
image_id = config.get('plugin', 'image_id')
command = config.get('plugin', 'command')
reference_value = config.getfloat('plugin', 'reference_value')
log_path = config.get('plugin', 'log_path')

scaling_parameters = {}

if scaler_plugin == 'progress-error':	
	actuator = config.get('scaler', 'actuator')
	starting_cap = config.get('scaler', 'starting_cap')
	metric_source = config.get('scaler', 'metric_source')
	check_interval = config.getint('scaler', 'check_interval')
	trigger_down = config.getint('scaler', 'trigger_down')
	trigger_up = config.getint('scaler', 'trigger_up')
	min_cap = config.getint('scaler', 'min_cap')
	max_cap = config.getint('scaler', 'max_cap')
	actuation_size = config.getint('scaler', 'actuation_size')
	metric_rounding = config.getint('scaler', 'metric_rounding')

	scaling_parameters = {'check_interval':check_interval,
					'trigger_down':trigger_down, 'trigger_up':trigger_up,
					'min_cap':min_cap, 'max_cap':max_cap,
					'actuation_size':actuation_size, 'metric_rounding':metric_rounding, 
					'actuator':actuator, 'metric_source':metric_source}
	
elif scaler_plugin == 'proportional':
	actuator = config.get('scaler', 'actuator')
	metric_source = config.get('scaler', 'metric_source')
	check_interval = config.getint('scaler', 'check_interval')
	trigger_down = config.getint('scaler', 'trigger_down')
	trigger_up = config.getint('scaler', 'trigger_up')
	min_cap = config.getint('scaler', 'min_cap')
	max_cap = config.getint('scaler', 'max_cap')
	metric_rounding = config.getint('scaler', 'metric_rounding')
	heuristic_name = config.get('scaler', 'heuristic_name')
	
	heuristic_options = {}
	heuristic_options['heuristic_name'] = heuristic_name
	
	if heuristic_name == "error_proportional":
		conservative_factor = config.getint('scaler', 'conservative_factor')
		heuristic_options['conservative_factor'] = conservative_factor

	scaling_parameters = {'check_interval':check_interval,
					'trigger_down':trigger_down, 'trigger_up':trigger_up,
					'min_cap':min_cap, 'max_cap':max_cap, 'metric_rounding':metric_rounding, 
					'actuator':actuator, 'metric_source':metric_source, 'heuristic_options': heuristic_options}

headers = {'Content-Type': 'application/json'}
body = dict(plugin=plugin, scaler_plugin=scaler_plugin,
	scaling_parameters=scaling_parameters, actuator=actuator, cluster_size=cluster_size,
	starting_cap=starting_cap, flavor_id=flavor_id, image_id=image_id, command=command,
	reference_value=reference_value, log_path=log_path)

url = "http://%s:%s/manager/execute" % (manager_ip, manager_port)
print "Making request to", url
body_log = body.copy()
print "Passing arguments as", body_log
r = requests.post(url, headers=headers, data=json.dumps(body))
print r.content
