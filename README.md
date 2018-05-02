# BIGSEA Asperathos - Broker

## Overview
The Broker component is the framework entry point for the user. It is responsible for receiving the user request and preparing its execution. On the process of executing a request, the broker is responsible for submitting the application for the execution infrastructure and interacts using REST API with all the other needed services that allow to monitor the application execution, to optimize the cluster size and to act on the cluster to provide assurance on meeting the application QoS.

## Requirements
* Python 2.7 or Python 3.5
* Linux packages: python-dev and python-pip
* Python packages: setuptools, tox and flake8

To **apt** distros, you can use [pre-install.sh](https://github.com/bigsea-ufcg/bigsea-manager/tree/refactor/docs/pre-install.sh) to install the requirements.

## Install
First of all, install **git**. After, you just need to clone the [Broker repository](https://github.com/bigsea-ufcg/bigsea-manager.git) in your machine.

### Configuration
A configuration file is required to run the Broker. Edit and fill your broker.cfg in the root of Broker directory. Make sure you have fill up all fields before run.
You can find a template in [config-example.md](https://github.com/bigsea-ufcg/bigsea-manager/tree/refactor/docs/config-example.md). 

### Run
In the Broker directory, start the service using tox command:
```
$ tox -e venv -- broker
```

## Avaliable plugins
* [Spark Sahara](https://github.com/bigsea-ufcg/bigsea-manager/tree/refactor/docs/plugins/spark_sahara.md)
* [Spark Mesos](https://github.com/bigsea-ufcg/bigsea-manager/tree/refactor/docs/plugins/spark_mesos.md)
* [Spark Generic](https://github.com/bigsea-ufcg/bigsea-manager/tree/refactor/docs/plugins/spark_mesos.md)
* [Openstack Generic](https://github.com/bigsea-ufcg/bigsea-manager/tree/refactor/docs/plugins/openstack_generic.md)
* [Chronos](https://github.com/bigsea-ufcg/bigsea-manager/tree/refactor/docs/plugins/chronos.md)

## Broker REST API
Endpoints is avaliable on [restapi-endpoints.md](https://github.com/bigsea-ufcg/bigsea-manager/tree/refactor/docs/restapi-endpoints.md) documentation.

## How to develop a plugin
See [plugin-development.md](https://github.com/bigsea-ufcg/bigsea-manager/tree/refactor/docs/plugin-development.md).
