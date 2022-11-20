"""
Me borrow some code from OpenStack Trove
For more details, see: https://opendev.org/openstack/trove
"""

import docker

from dockeraken.configs import cfg
from typing import Any, Union, Optional


class DockerUtils():
    _docker_client: docker.DockerClient

    def __init__(self):
        pass

    @property
    def client(self):
        if self._docker_client:
            return self._docker_client

        self._docker_client = docker.from_env()
        return self._docker_client

    def login(self, container_registry, username, password):
        self.client.login(username, password, registry=container_registry)

    def list_containers(self):
        return self.client.containers.list()

    def stop_container(
            self,
            name: str,
            timeout=cfg.default_stop_container_timeout_in_seconds):
        container: Any = self.client.containers.get(name)
        container.stop(timeout=timeout)

    def start_container(self,
                        image,
                        name: str,
                        restart_policy="unless-stopped",
                        volumes={},
                        ports={},
                        user="",
                        network_mode="host",
                        environment={},
                        command=""):
        """Start a docker container.

        :param image: docker image.
        :param name: container name.
        :param restart_policy: restart policy.
        :param volumes: e.g.
            {"/host/trove": {"bind": "/container/trove", "mode": "rw"}}
        :param ports: ports is ignored when network_mode="host". e.g.
            {"3306/tcp": 3306}
        :param user: e.g. "1000.1001"
        :param network_mode: One of bridge, none, host
        :param environment: Environment variables
        :param command:
        :return:
        """
        try:
            container: Any = self.client.containers.get(name)
            container.start()
        except docker.errors.NotFound:  # type: ignore
            container = self.client.containers.run(
                image,
                name=name,
                restart_policy={"Name": restart_policy},
                privileged=False,
                network_mode=network_mode,
                detach=True,
                volumes=volumes,
                ports=ports,
                user=user,
                environment=environment,
                command=command)

        return container

    def run_container(self,
                      image: str,
                      name: Optional[str],
                      network=None,
                      network_mode: Optional[str] = "host",
                      user="",
                      volumes={},
                      environment={},
                      command="",
                      detach=True,
                      remove=False):
        """Run command in a container and return the string output list.

        :param image: docker image.
        :param name: container name.
        :param volumes: e.g.
            {"/host/trove": {"bind": "/container/trove", "mode": "rw"}}
        :param user: e.g. "1000.1001"
        :param network_mode: One of bridge, none, host
        :param environment: Environment variables
        :param command:
        :return:
        """
        try:
            container: Any = self.client.containers.get(name)
            container.remove(force=True)
        except docker.errors.NotFound:  # type: ignore
            pass

        kwargs: dict = {
            "name": name,
            "volumes": volumes,
            "remove": remove,
            "command": command,
            "user": user,
            "detach": detach,
            "environment": environment
        }

        # network param is incompatible with network_mode
        if network:
            kwargs["network"] = network
        else:
            kwargs["network_mode"] = network_mode

        container = self.client.containers.run(image, **kwargs)

        # need reload to get container info
        # because of detach=True
        # more details see https://docker-py.readthedocs.io/en/stable/containers.html#container-objects
        container.reload()

        return container

    def restart_container(
            self,
            name,
            timeout=cfg.default_stop_container_timeout_in_seconds):
        container: Any = self.client.containers.get(name)
        container.restart(timeout=timeout)

    def remove_container(self, name):
        try:
            container: Any = self.client.containers.get(name)
            container.remove(force=True)
        except docker.errors.NotFound:  # type: ignore
            pass

    def prune_images(self):
        """Remove unused images."""
        self.client.images.prune(filters={"dangling": False})

    def create_network(self, name, driver="bridge", opts=None):
        return self.client.networks.create(name, driver, opts)

    def get_container_ip(self, name, network=None):
        container: Any = self.client.containers.get(name)
        network_settings = container.attrs["NetworkSettings"]["Networks"]
        print(network_settings)

        if network:
            return network_settings[network]["IPAddress"]

        first_network = list(network_settings.keys())[0]

        return network_settings[first_network]["IPAddress"]
