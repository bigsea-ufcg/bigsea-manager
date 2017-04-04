import monascaclient.exc as exc
import time
import requests
import ConfigParser

from monascaclient import client as monclient, ksclient

HOST_CPU_METRIC = 'host.cpu'
HOST_RAM_METRIC = 'host.ram'
VM_CPU_METRIC = 'vm.cpu'
VM_RAM_METRIC = 'vm.ram'
JOB_PROGRESS_METRIC = "job.progress"
ELAPSED_TIME_METRIC = "elapsed2"
EXPECTED_TIME = 5000.0


class MonascaMonitor():

    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('./manager.cfg')

        self.monasca_endpoint = config.get('monasca', 'monasca_endpoint')
        self.monasca_username = config.get('monasca', 'username')
        self.monasca_password = config.get('monasca', 'password')
        self.monasca_auth_url = config.get('monasca', 'auth_url')
        self.monasca_project_name = config.get('monasca', 'project_name')
        self.monasca_api_version = config.get('monasca', 'api_version')

    def get_host_cpu_utilization(self, dimensions):
        return self.get_measurements(HOST_CPU_METRIC, dimensions)

    def get_vm_cpu_utilization(self, dimensions):
        return self.get_measurements(VM_CPU_METRIC, dimensions)

    def get_title(self):
        return 'Monasca Monitor'

    def get_vm_ram_utilization(self, dimensions):
        return self.get_measurements(VM_RAM_METRIC, dimensions)

    def get_host_ram_utilization(self, dimensions):
        return self.get_measurements(HOST_RAM_METRIC, dimensions)

    def get_job_progress(self, dimensions):
        return self.get_measurements(JOB_PROGRESS_METRIC, dimensions)

    def get_measurements(self, metric_name, dimensions):
        measurements = []
        try:
            monasca_client = self._get_monasca_client()
            dimensions = {'application_id': dimensions['application_id'],
                          'service': dimensions['service']}
            measurements = monasca_client.metrics.list_measurements(
                name=metric_name, dimensions=dimensions,
                start_time='2014-01-01T00:00:00Z', debug=False)
        except exc.HTTPException as httpex:
            print httpex.message
        except Exception as ex:
            print ex.message
        if len(measurements) > 0:
            return measurements[0]['measurements']
        else:
            return None

    def first_measurement(self, name, dimensions):
        if self.get_measurements(name, dimensions) is not None:
            return self.get_measurements(name, dimensions)[0]
        return [None, None, None]

    def last_measurement(self, name, dimensions):
        if self.get_measurements(name, dimensions) is not None:
            return self.get_measurements(name, dimensions)[-1]
        return [None, None, None]

    def get_used_time(self):
        return self.get_measurements(ELAPSED_TIME_METRIC) / EXPECTED_TIME

    def get_completion_used_time_diff(self, job_name):
        completion = self.get_job_progress(job_name)
        used_time = self.get_used_time()

        if completion != 0:
            diff = completion - used_time

    def _get_monasca_client(self):

        # Authenticate to Keystone
        ks = ksclient.KSClient(
            auth_url=self.monasca_auth_url,
            username=self.monasca_username,
            password=self.monasca_password,
            project_name=self.monasca_project_name,
            debug=False
        )

        # Monasca Client
        monasca_client = monclient.Client(self.monasca_api_version,
                                          ks.monasca_url,
                                          token=ks.token,
                                          debug=False)

        return monasca_client

    def send_metrics(self, measurements):

        batch_metrics = {'jsonbody': measurements}
        try:
            monasca_client = self._get_monasca_client()
            monasca_client.metrics.create(**batch_metrics)
        except exc.HTTPException as httpex:
            print httpex.message
        except Exception as ex:
            print ex.message
