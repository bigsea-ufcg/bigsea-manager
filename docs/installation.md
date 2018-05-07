## Requirements
* Python 2.7 or Python 3.5
* Linux packages: python-dev and python-pip
* Python packages: setuptools, tox and flake8

To **apt** distros, you can use [pre-install.sh](https://github.com/bigsea-ufcg/bigsea-manager/tree/refactor/tools/pre-install.sh) to install the requirements.

## Install
First of all, install **git**. After, you just need to clone the [Broker repository](https://github.com/bigsea-ufcg/bigsea-manager.git) in your machine.

### Configuration
A configuration file is required to run the Broker. **Edit and fill your broker.cfg in the root of Broker directory.** Make sure you have fill up all fields before run.
You can find a template in [config-example.md](https://github.com/bigsea-ufcg/bigsea-manager/tree/refactor/docs/config-example.md). 

### Run
In the Broker root directory, start the service using tox command:
```
$ tox -e venv -- broker
```
