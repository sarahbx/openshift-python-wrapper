from openshift.dynamic.exceptions import NotFoundError

from ocp_resources.resource import NamespacedResource


class PackageManifest(NamespacedResource):
    api_group = NamespacedResource.ApiGroup.PACKAGES_OPERATORS_COREOS_COM

    def __init__(self, name, namespace, label_selector, **kwargs):
        super().__init__(name=name, namespace=namespace, **kwargs)
        self.label_selector = label_selector

    @property
    def field(self):
        for resource_field in self.__class__.get(
            dyn_client=self.privileged_client or self.client,
            namespace=self.namespace,
            field_selector=f"metadata.name={self.name}",
            label_selector=self.label_selector,
            raw=True,
        ):
            return resource_field

        raise NotFoundError(
            f"No PackageManifest found in {self.namespace} "
            f"with name {self.name} and labels {self.label_selector}"
        )

    @property
    def instance(self):
        raise NotImplementedError(
            f"instance() not available, please use {self.__class__.__name__}.field"
        )

    def to_dict(self):
        raise NotImplementedError("to_dict() not available")
