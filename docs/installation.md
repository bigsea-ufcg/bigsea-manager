## Requirements
* Python 2.7
* Linux packages: python-dev and python-pip
* Python packages: setuptools, tox and flake8

To **apt** distros, you can use [pre-install.sh](https://github.com/bigsea-ufcg/bigsea-manager/tree/master/setup.sh) to install the requirements.

## Install
Clone the [Broker repository](https://github.com/bigsea-ufcg/bigsea-manager.git) in your machine.

### Configuration
A configuration file is required to run the Broker. **Edit and fill your broker.cfg in the root of Broker directory.** Make sure you have fill up all fields before run.
You can find a template in [config-example.md](https://github.com/bigsea-ufcg/bigsea-manager/tree/master/docs/config-example.md). 

### Run
In the Broker root directory, start the service using run script:
```
$ ./run.sh
```

Or using tox command:
```
$ tox -e venv -- broker
```
