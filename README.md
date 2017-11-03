# Manager/Broker - EUBra-BIGSEA WP3
The Manager component is the framework entry point for the user. It is responsible for receiving the user request and preparing its execution. On the process of executing a request, the broker is responsible for submitting the application for the execution infrastructure and interacts using REST API with all the other needed services that allow to monitor the application execution, to optimize the cluster size and to act on the cluster to provide assurance on meeting the application QoS.

# Table of Contents
--------
- [Architecture description](#architecture-description)
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

# Deploy
To install, configure and run the Manager component you will need a virtual machine with the configurations described below.

**Minimal configuration**
```
OS: Ubuntu 14.04
CPU: 1 core
Memory: 2GB of RAM
Disk: there is no disk requirements.
```

In the virtual machine that you want to install the broker follow the steps below:

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
| 200 | Normal response code |

#### Request parameters
##### Manager
| Name | Type | Description |
| --- | --- | --- |
| plugin | string | The broker plugin. |

##### Cluster
| Name | Type | Description |
| --- | --- | --- |
| opportunism | boolean | If set to true, enables opportunism. |
| size | int | The size of cluster that will be created. |
| flavor_id | string | The openstack flavor of cluster. |
| image_id | string | The openstack image of cluster. |
| master_ng | string | ID of master node group. |
| slave_ng | string | ID of slave node group. |
| opportunistic_slave_ng | string | ID of opportunistic slave node group. |

##### Infrastructure
| Name | Type | Description |
| --- | --- | --- |
| net_id | string | ID of openstack network. |

##### Authorizer
| Name | Type | Description |
| --- | --- | --- |
| username  | string | Username of authorizer. |
| password  | string | Password of authorizer. |

##### Job submission
| Name | Type | Description |
| --- | --- | --- |
| args | string | Spark arguments of job submission (accept Swift and HDFS paths). |
| dependencies | string | Dependencies of job (separated by comma). |
| main_class | string | If the job is Java, set the main class of job binary. |
| binary_url | string | Job binary url (accept Swift and HDFS paths). |
| template_name | string | Name of job template (Swift submission parameter). |
| binary_name | string | Name of job binary (Swift submission parameter). |
| openstack_plugin | string | Job plugin. |
| plugin_version | string | Version of job plugin. |
| type | string | Job type. |

##### Monitor
| plugin_app | string | Monitor plugin |
| expected_time | int | Expected application time. |
| collect_period | int | Collect period of Monitor component. |
| number_of_jobs | int | Number of jobs of Spark application. |

##### Controller
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
   "cluster":{
      "slave_ng":"acb2d6aa-858e-40e4-b436-cc195506e819",
      "image_id":"96e4df4d-2398-4330-99d8-e030d689a226",
      "opportunism":"False",
      "master_ng":"89428c9c-2b4d-4a63-8c85-68d778b0c715",
      "flavor_id":"89789ded-183b-4a75-b7e9-5467d6fc944f",
      "opportunistic_slave_ng":"acb2d6aa-858e-40e4-b436-cc195506e819",
      "size":1
   },
   "job":{
      "plugin_version":"2.1.0",
      "openstack_plugin":"spark",
      "template_name":"myapp",
      "args":"hdfs://192.168.1.75/myinput.csv hdfs://10.11.4.222/myoutput.csv",
      "dependencies":"package1,package2",
      "binary_name":"",
      "main_class":"Package.MainClass",
      "type":"Spark",
      "binary_url":"hdfs://10.11.4.222/mybinary.jar"
   },
   "authorizer":{
      "username":"bob",
      "password":"alice"
   },
   "monitor":{
      "expected_time":"100",
      "number_of_jobs":"5",
      "collect_period":"5",
      "plugin_app":"spark_progress"
   },
   "scaler":{
      "starting_cap":"80",
      "application_type":"os_generic",
      "scaler_plugin":"progress-error",
      "metric_rounding":2,
      "trigger_up":10,
      "trigger_down":10,
      "actuation_size":15,
      "max_cap":100,
      "check_interval":10,
      "metric_source":"monasca",
      "actuator":"service",
      "min_cap":20
   },
   "broker":{
      "plugin":"sahara"
   },
   "infra":{
      "net_id":"64ee4355-4d7f-4170-80b4-5e8348af6a61"
   }
}
```

#### Response parameters
| Name | Type | Description |
| --- | --- | --- |
| execution_id | string | UUID of submitted application. |

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
