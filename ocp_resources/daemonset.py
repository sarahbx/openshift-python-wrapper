import kubernetes

from ocp_resources.constants import PROTOCOL_ERROR_EXCEPTION_DICT, TIMEOUT_4MINUTES
from ocp_resources.logger import get_logger
from ocp_resources.resource import NamespacedResource
from ocp_resources.utils import TimeoutSampler


LOGGER = get_logger(name=__name__)


class DaemonSet(NamespacedResource):
    """
    DaemonSet object.
    """

    api_group = NamespacedResource.ApiGroup.APPS

    def wait_until_deployed(self, timeout=TIMEOUT_4MINUTES):
        """
        Wait until all Pods are deployed and ready.

        Args:
            timeout (int): Time to wait for the Daemonset.

        Raises:
            TimeoutExpiredError: If not all the pods are deployed.
        """
        self.wait_for_pods(scheduled=True, timeout=timeout)

    def wait_for_pods(self, scheduled=True, timeout=TIMEOUT_4MINUTES):
        """
        Wait until all pods are updated.

        Args:
            scheduled (bool): True for pods scheduled, False for not scheduled.
            timeout (int): Time to wait for the daemonset.

        Raises:
            TimeoutExpiredError: If conditions do not match within timeout
        """
        LOGGER.info(f"Wait for {self.kind} {self.name} to be scheduled: {scheduled}")
        samples = TimeoutSampler(
            wait_timeout=timeout,
            sleep=1,
            exceptions_dict=PROTOCOL_ERROR_EXCEPTION_DICT,
            func=self.api.get,
            field_selector=f"metadata.name=={self.name}",
        )
        for sample in samples:
            if sample.items:
                instance = sample.items[0]
                status = instance.status

                desired_number_scheduled = status.desiredNumberScheduled or 0
                updated_number_scheduled = status.updatedNumberScheduled or 0
                current_number_scheduled = status.currentNumberScheduled or 0
                number_misscheduled = status.numberMisscheduled or 0
                number_available = status.numberAvailable or 0
                number_ready = status.numberReady or 0

                if (
                    (scheduled and desired_number_scheduled)
                    and desired_number_scheduled
                    == updated_number_scheduled
                    == current_number_scheduled
                    == number_available
                    == number_ready
                    and number_misscheduled == 0
                ) or not (
                    scheduled
                    or desired_number_scheduled
                    or current_number_scheduled
                    or number_available
                    or number_ready
                    or number_misscheduled
                ):
                    return

    def delete(self, wait=False, timeout=TIMEOUT_4MINUTES, body=None):
        """
        Delete Daemonset

        Args:
            wait (bool): True to wait for Daemonset to be deleted.
            timeout (int): Time to wait for resource deletion
            body (dict): Content to send for delete()

        Returns:
            bool: True if delete succeeded, False otherwise.
        """
        super().delete(
            wait=wait,
            timeout=timeout,
            body=kubernetes.client.V1DeleteOptions(propagation_policy="Foreground"),
        )
