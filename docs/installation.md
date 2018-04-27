# Installation

## Requirements
* Python 2.7 or Python 3.5
* Linux packages: python-dev and python-pip
* Python packages: setuptools, tox and flake8
* Works on Linux

## Install
First of all, install **git** in your machine. After, to a simple install of Broker component, you just need to clone the Broker repository (https://github.com/bigsea-ufcg/bigsea-manager.git) in your machine.

## Configuration
A configuration file is required to run the Broker. You can find a template in the **config-example.md**, rename the template to broker.cfg. Make sure you have fill up all fields before run.

## Run
In the Broker directory, start the service using tox command:
```
$ tox -e venv -- broker
```
