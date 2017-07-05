# BigSea Manager
This is the webservice responsible for linking the Client/User with the execution unit. At this point, the execution unit is only OpenStack Sahara running a Spark Cluster.

## Deploying the Manager
To configure and deploy the Broker component we need a virtual machine with the configurations described below.

#### Minimal configuration:
- OS: Ubuntu 14.04
- CPU: 1 core
- Memory: 2GB of RAM
- Disk: there is no disk requirements.

In the virtual machine that you want to install the manager follow the steps below:

#### Install git
```bash
$ sudo apt-get install git
```

#### Clone the BigSea Manager repository
```bash
$ git clone https://github.com/bigsea-ufcg/bigsea-manager 
```

#### Access the bigsea manager folder and run the setup script
```bash
$ cd bigsea-manager/
$ ./setup.sh # You must run this command as superuser to install some requirements
```

#### Write a configuration file (manager.cfg) with the required informations contained into manager.cfg.template and start the service
```bash
$ ./run.sh
```

## Using Manager API

The broker has 4 entrances on its API.
 
1. **POST <broker-ip:port>/manager/execute:** This call expects a JSON on the body with the client’s specification of the application to run. This body should look like this:

```
{
   "opportunistic": <boolean>,
   "cluster_size": <int>,
   "bigsea_username": <bs_username>,
   "bigsea_password": <bs_password>,
   "plugin": <plugin_name>,
   "collect_period": <seconds_int>,
   "scaling_parameters": {
      "starting_cap": <percent_int>,
      "actuator": <actuator_name>,
      "metric_rounding": <int>,
      "trigger_up": <percent_int>,
      "trigger_down": <percent_int>,
      "actuation_size": <percent_int>,
      "max_cap": <percent_int>,
      "check_interval": <seconds_int>,
      "metric_source": "monasca",
      "min_cap": 20
   },
  "info_plugin": {
      "key1": value1,
      "key2": value2,
      …
      "keyx": valuex
   }
}
```
 
- scaling_parameters:
  - starting_cap: initial CPU cap percentage of the machines that compose the cluster;
  - actuator: name of the actuator plugin that must be used;
  - trigger_up: upper bound to scale up based on the error;
  - trigger_down: lower bound to scale up based on the error;
  - actuation_size: percentage of CPU cap to be increased to the machines;
  - max_cap: maximum percentage for the machine’s CPU cap;
  - check_interval: period between each evaluation of the error to take scaling decisions (scale up/down);
  - metric_source: metric storage service;
  - min_cap: minimum percentage for the machine’s CPU cap.
 
2. **POST <broker-ip:port>/manager/stop_app/<app_id>:** This call expects only the <app_id> and it stops it execution.
 
3. **POST <broker-ip:port>/manager/kill_all:** This will kill all running applications.
 
4. **POST <broker-ip:port>/manager/status:** Return the status from all running applications.


## Creating a Broker plugin

1. Create a new folder under *application_manager/plugins* with the desired plugin name and add *__init__.py*. In this tutorial, we will use Fake as the plugin name
 
2. Write a new python class under *application_manager/plugins/fake*
 
It must implement the methods *get_title*, *get_description*, *to_dict* and *execute*.
 
- **get_title(self)**
  - Returns plugin title
 
- **get_description(self)**
  - Returns plugin description
 
- **to_dict(self)**
  - Return a dict with the plugin information, name, title and description
 
- **execute(self, data)**
  - Actually execute the logic of cluster creation and job execution
  - Returns information if the execution was successful or not
    
#### Example:

```
from application_manager.plugins import base

class FakeProvider(base.PluginInterface):

    def get_title(self):
        return 'Fake Plugin '

    def get_description(self):
        return 'Fake Plugin'

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.get_title(),
            'description': self.get_description(),
        }
    def execute(self, data):
        return True
```
 
3. Add the new plugin to *setup.py* under entry_points:

```
    entry_points={
        'console_scripts': [
            'application_manager=application_manager.cli.main:main',
        ],
        'application_manager.execution.plugins': [
            'sahara=application_manager.plugins.sahara.plugin:SaharaProvider',
            'fake=application_manager.plugins.test_plugin.plugin:FakeProvider',
        ],
```
 
4. Under *manager.cfg* add the plugin to the list of desired plugins:

```
[services]
 
monitor_url = 
controller_url =
plugins = os_generic,sahara,fake
```
 
Note: Make sure that the name matches under *setup.py* and the *manager.cfg* otherwise the plugin won’t be loaded.
