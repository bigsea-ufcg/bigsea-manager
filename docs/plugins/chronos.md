Chronos enables the execution of periodic jobs that need to be scheduled for a specific time frame. It uses the ISO 8601 format to define the periodicity of the jobs. In the context of the project, we use Chronos to program tasks that iterate repeatedly so we can easily obtain the progress achieved by a task.

The Broker requests the Monitor & Controller in the init of a job execution. It sends the required information for the elasticity to the Monitor & Controller. Finally, it sends the job to the Chronos Framework. The Broker uses online Chronos REST clients. 
