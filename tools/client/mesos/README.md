The Mesos plugin enables the submission of a Spark application over Mesos in an infrastructure provided by OpenNebula. There are some points that are very specific to work with the infrastructure security limitations that we have in the context of BigSea EuBra partners. It means that this plugin is not completely generic, because it works following the GryCAP network topology and security policies. But this is a great base to write any other plugin to do similar tasks.

This plugin submit (via ssh) an spark application with the input and output stored in some accessible HDFS. The job binary must be in a public download link or also stored in the HDFS. It also can enable the QoS monitor and the controller services, described in the submission configuration file (JSON).

To submit a Spark application with Spark-Mesos plugin, use example.json as an example and execute this command:
```curl -X POST  -H "Accept: Application/json" -H "Content-Type: application/json" http://ip:port/manager/execute -d @example.json```
