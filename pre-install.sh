#!/bin/bash

sudo apt-get update
sudo apt-get -y install python-dev
sudo apt-get -y install python-pip
sudo pip install setuptools
sudo pip install tox
sudo pip install flake8
