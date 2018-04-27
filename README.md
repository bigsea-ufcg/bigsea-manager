# Broker

## Overview
The Broker component is the framework entry point for the user. It is responsible for receiving the user request and preparing its execution. On the process of executing a request, the broker is responsible for submitting the application for the execution infrastructure and interacts using REST API with all the other needed services that allow to monitor the application execution, to optimize the cluster size and to act on the cluster to provide assurance on meeting the application QoS.

### Architecture
Is implemented following a plugin architecture, providing flexibility to add or remove plugins when necessary. All the integrations with different infrastructures and components are made by specific plugins, so the different technologies in the context of the framework can be easily integrated by the Broker service.

## Installation
### Requirements
* Python 2.7 or Python 3.5
* Linux packages: python-dev and python-pip
* Python packages: setuptools, tox and flake8
* Works on Linux

To **apt** distros, you can use [pre-install.sh](bigsea-manager/tools/pre-install.sh) to install the requirements.

### Install
First of all, install **git** in your machine. After, you just need to clone the [Broker repository](https://github.com/bigsea-ufcg/bigsea-manager.git) in your machine.

### Configuration
A configuration file is required to run the Broker. Edit and fill your broker.cfg in the root of Broker directory. Make sure you have fill up all fields before run.
You can find a template in [config-example.md](bigsea-manager/docs/config-example.md). 

### Run
In the Broker directory, start the service using tox command:
```
$ tox -e venv -- broker
```

## Broker REST API
Endpoints is avaliable on [restapi-endpoints.md](bigsea-manager/docs/restapi-endpoints.md) documentation.

## Plugin development
See [plugin-development.md](bigsea-manager/docs/plugin-development.md).
