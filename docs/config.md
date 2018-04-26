# Configuration

## Example: 
```
[services]
controller_url =
monitor_url =
optimizer_url =
authorization_url =

[general]
port =
plugins = plugin1,plugin2,plugin3
hosts = compute1,compute2,compute3

[os-generic]
public_key =
key_path = 
log_path =
user =
password =
auth_ip =
project_id =
user_domain_name =

[spark-generic]
swift_container =
swift_logdir =
remote_hdfs =
number_of_attempts =
public_key =
key_path =
log_path =
user =
password =
auth_ip =
project_id =
user_domain_name =
masters_ips =

[spark-sahara]
swift_container =
swift_logdir =
remote_hdfs =
number_of_attempts =
public_key =
key_path =
log_path =
user =
password =
auth_ip =
project_id =
user_domain_name =
dummy_opportunistic =

[spark-mesos]
mesos_url =
mesos_port =
cluster_username =
cluster_password =
key_path =
one_url =
one_username =
one_password =
spark_path =

[chronos]
url =
username =
password =
supervisor_ip =
```
