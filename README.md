# BigSea WP3 - Manager
The Manager component is the framework entry point for the user. It is responsible for receiving the user request and preparing its execution. On the process of executing a request, the broker is responsible for submitting the application for the execution infrastructure and interacts using REST API with all the other needed services that allow to monitor the application execution, to optimize the cluster size and to act on the cluster to provide assurance on meeting the application QoS.

# Table of Contents
--------
- [Architecture description](#architecture-description)
- [Dependencies](#dependencies)
- [Deploy](#deploy)
  - [Install](#install)
  - [Configure](#configure)
  - [Run](#run)
- [API usage](#api-usage)
  - [General information](#general-information)
  - [Run example](#run-example)
  - [Endpoints](#endpoints)
    - [Execute application](#execute-application)
    - [Stop application](#stop-application)
    - [Kill applications](#kill-applications)
    - [List applications status](#list-applications-status)
- [Plugin creation](#plugin-creation)
- [License](#license)

# Architecture description
--------
The Manager is implemented following a plugin architecture, providing flexibility to add or remove plugins when necessary. All the integrations with different infrastructures and components are made by specific plugins, so the different technologies in the context of EUBra-BIGSEA framework can be easily integrated by the broker service.

# Dependencies
--------
To have your Manager working properly you need to ensure that it has access to following components in your infrastructure:

* **OpenStack Compute Service** - *Nova* (with admin privileges)
* **OpenStack Monitoring Service** - *Monasca*

# Deploy
To install, configure and run the Manager component you will need a virtual machine with the configurations described below.

**Minimal configuration**
```
OS: Ubuntu 14.04
CPU: 1 core
Memory: 2GB of RAM
Disk: there is no disk requirements.
```

In the virtual machine that you want to install the manager follow the steps below:

## Install
1. Install git
    ```bash
    $ sudo apt-get install git
    ```
2. Clone the BigSea Manager repository
    ```bash
    $ git clone https://github.com/bigsea-ufcg/bigsea-manager.git
    ```
3. Access the bigsea-manager folder and run the setup script
    ```bash
    $ ./setup.sh # You must run this command as superuser to install some requirements
    ```
## Configure
A configuration file is required to run the Manager. You can find a template in the main directory called manager.cfg.template, rename the template to manager.cfg or any other name you want. Make sure you have fill up all fields before run.
```
[services]

monitor_url = http://<monitor-ip>:<monitor-port>
controller_url = http://<controller-ip>:<controller-port>
authorization_url = <authorizer_url>
optimizer_url = <optimizer_url>
plugins = <plugin_1>,<plugin_2>,...,<plugin_n>

[credentials]

public_key = <public_key_name>
key_path = <private_key_path>
user = <cloud_user>
password = <cloud_password>
auth_ip = <cloud_url>
project_id = <cloud_project_id>
user_domain_name = <cloud_domain_name>
log_path = <manager_log_path>
swift_container = <swift_container_name>

[infra]

hosts = <host_1> <host_2> ... <host_n>
```

## Run
Start the service running the run.sh script.
```
$ ./run.sh
```

# API usage
--------
## General information
This section defines the API usage. 

## Run example
You can submit your requests by using curl command, example:
```
curl -H "Content-Type: application/json" -X POST --data @your_json.json http://url_or_ip:1514/manager/execute
```

## Endpoints
### Execute application
`POST manager/execute`

This call expects a JSON on the body with the client’s specification of the application to run.

#### Response codes
| Code | Reason |
| --- | --- |
| 200 |  |
| 500 |  |

#### Request parameters
| Name | Type | Description |
| --- | --- | --- |
| plugin | string |  |
| cluster_size | int |  |
| bigsea_username | string |  |
| bigsea_password | string |  |
| opportunistic | boolean |  |
| args | string |  |
| main_class | string |  |
| scaler_plugin | string |  |
| flavor_id | string |  |
| image_id | string |  |
| job_template_name | string |  |
| job_binary_name | string |  |
| job_binary_url | string |  |
| input_ds_id | string |  |
| output_ds_id | string |  |
| plugin_app | string |  |
| expected_time | int |  |
| collect_period | int |  |
| openstack_plugin | string |  |
| version | string |  |
| job_type | string |  |
| cluster_id | string |  |
| master_ng | string |  |
| slave_ng | string |  |
| net_id | string |  |
| starting_cap | int |  |
| actuator | string |  |
| metric_source | string |  |
| application_type | string |  |
| check_interval | int |  |
| trigger_down | int |  |
| trigger_up | int |  |
| min_cap | int |  |
| max_cap | int |  |
| actuation_size | int |  |
| metric_rounding | int |  |

#### Request example
```
{  
   "plugin":"sahara",
   "scaler_plugin":"progress-error",
   "cluster_size":10,
   "flavor_id":"7e0a0241-72de-4773-9ef2-cfb38ecfdb82",
   "image_id":"f2530513-6286-4907-b313-f417d8d703ce",
   "bigsea_username":"my_username",
   "bigsea_password":"my_password",
   "opportunistic":"False",
   "args":["swift://bigsea-ex/EMaaS/input/shapes.csv", "swift://bigsea-ex/EMaaS/input/gps_data_5d.csv", "swift://bigsea-ex/EMaaS/output/output_1843768234769",  "10"],
   "main_class":"LineMatching.MatchingRoutesShapeGPS",
   "job_template_name":"EMaaS",
   "job_binary_name":"EMaaS",
   "job_binary_url":"swift://bigsea-ex/EMaaS/EMaaS.jar",
   "input_ds_id":"",
   "output_ds_id":"",
   "plugin_app":"spark_progress",
   "expected_time":100,
   "collect_period":5,
   "openstack_plugin":"spark",
   "version":"1.6.0",
   "job_type":"Spark",
   "cluster_id":"",
   "master_ng":"ffb464df-d06e-49ce-afd6-fed4e14260fb",
   "slave_ng":"2f0f946e-2bdb-43b0-add0-e3bbbca1d5c4",
   "net_id":"64ee4355-4d7f-4170-80b4-5e8348af6a61",
   "starting_cap":50,
   "actuator":"service",
   "scaling_parameters":{  
      "metric_source":"monasca",
      "application_type":"os_generic",
      "check_interval":10,
      "trigger_down":10,
      "trigger_up":10,
      "min_cap":20,
      "max_cap":100,
      "actuation_size":15,
      "metric_rounding":2
   }
}
```

#### Response parameters
| Name | Type | Description |
| --- | --- | --- |
| execution_id | string |  |

#### Response example
```
{  
   "execution_id":"osspark04"
}
```

### Stop application
`POST manager/stop_app/:app_id`

This call expects only the *:app_id* and it stops it execution.

### Kill applications
`POST manager/kill_all`

This will kill all running applications.

### List applications status
`POST manager/status`

Return the status from all running applications.

# Plugin creation
--------
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
