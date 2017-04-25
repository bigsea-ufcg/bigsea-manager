# BigSea Manager

This is the webservice responsible for linking the Client with the execution unit.
At this point, the execution unit is only OpenStack Sahara running a Spark Cluster.

# Deploying the Manager
```bash
git clone https://github.com/bigsea-ufcg/bigsea-manager.git
cp manager.cfg.template manager.cfg
```

Update manager.cfg with necessary credentials and environement information
```bash
./run.sh
```

