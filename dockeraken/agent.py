from typing import Union, Optional
from dockeraken.utils.docker_utils import DockerUtils


class Agent:
    docker_utils: DockerUtils

    def __init__(self):
        pass

    def run(self,
            image: str,
            name: Optional[str] = None,
            network: Optional[str] = None,
            network_mode: Optional[str] = "host"):
        container = self.docker_utils.run_container(image=image,
                                                    name=name,
                                                    network=network,
                                                    network_mode=network_mode)
        return container

    def list_containers(self):
        return self.docker_utils.list_containers()

    def get_container_ip(self, name: Optional[str], network: Optional[str]):
        ip = self.docker_utils.get_container_ip(name, network)
        return ip