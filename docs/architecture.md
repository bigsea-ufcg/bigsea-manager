# Architecture description
The Broker is implemented following a plugin architecture, providing flexibility to add or remove plugins when necessary. All the integrations with different infrastructures and components are made by specific plugins, so the different technologies in the context of the framework can be easily integrated by the Broker service.

## Asperathos framework execution workflow
![Flow](https://github.com/bigsea-ufcg/bigsea-manager/blob/refactor/docs/flow.png)

1. Submit application
2. Prepare infrastructure to run application
3. Start monitor
4. Start controller
5. Collect metrics
6. Publish metrics
7. Get application metrics
8. Act on infrastructure
