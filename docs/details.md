# Description
On the process of executing a request, the broker is responsible for submitting the application for the execution infrastructure and interacts using REST API with all the other needed services that allow to monitor the application execution, to optimize the cluster size and to act on the cluster to provide assurance on meeting the application QoS.

# Architecture
The broker is implemented following a plugin architecture, providing flexibility to add or remove plugins when necessary. All the integrations with different infrastructures and components are made by specific plugins, so the different technologies in the context of EUBra-BIGSEA framework can be easily integrated by the broker service.
