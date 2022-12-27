import os
import sys
import pika
import json
import time
import traceback
import logging
import argparse
import configparser
import threading

from typing import Any, List
from dockeraken.configs import cfg
from dockeraken.configs import exchname
from dockeraken.utils.docker import DockerUtils

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",
                    level=logging.INFO)

parser = argparse.ArgumentParser(prog="dockeraken")

parser.add_argument("-c",
                    "--config",
                    help="Dockeraken config path",
                    required=True,
                    type=str)


def main():
    args = parser.parse_args()
    config_parser = configparser.ConfigParser()
    config_parser.read(args.config)

    for section in config_parser.sections():
        cfg.dockeraken_id = config_parser[section]["dockeraken_id"]
        cfg.transport_url = config_parser[section]["transport_url"]

    docker_utils = DockerUtils()
    logging.info(f"dockeraken_id {cfg.dockeraken_id}")

    available_methods = []
    for m in dir(docker_utils):
        if (not m.startswith("_")) and (callable(getattr(docker_utils, m))):
            available_methods.append(m)

    def callback(ch, method, properties, body):
        try:
            logging.info(" [x] Received %r" % body)
            payload = json.loads(body)
            action = getattr(docker_utils, payload["method"])
            action(**payload)
        except Exception as e:
            logging.error(traceback.format_exc())

        ch.basic_ack(delivery_tag=method.delivery_tag)

    stop = False

    def send_available_methods():
        conn = pika.BlockingConnection(pika.URLParameters(cfg.transport_url))
        channel = conn.channel()
        channel.exchange_declare(exchname.available_methods,
                                 exchange_type="fanout")
        try:
            while not stop:
                payload = {
                    "dockeraken_id": cfg.dockeraken_id,
                    "available_methods": available_methods
                }

                channel.basic_publish(exchange=exchname.available_methods,
                                      routing_key="",
                                      body=json.dumps(payload))
                time.sleep(3)
        except Exception as e:
            logging.error(traceback.format_exc())

    def send_current_containers():
        conn = pika.BlockingConnection(pika.URLParameters(cfg.transport_url))
        channel = conn.channel()
        channel.exchange_declare(exchname.current_containers,
                                 exchange_type="fanout")
        try:
            while not stop:
                current_containers = []
                raw_containers: List[Any] = docker_utils.list_containers(
                    all=True)

                for e in raw_containers:
                    c = {
                        "id": e.id,
                        "short_id": e.short_id,
                        "name": e.name,
                        "image": {
                            "tags": e.image.tags,
                        },
                        "status": e.status,
                    }
                    current_containers.append(c)
                payload = {
                    "dockeraken_id": cfg.dockeraken_id,
                    "current_containers": current_containers
                }

                channel.basic_publish(exchange=exchname.current_containers,
                                      routing_key="",
                                      body=json.dumps(payload))
                time.sleep(3)
        except Exception as e:
            logging.error(traceback.format_exc())

    threading.Thread(target=send_available_methods).start()
    threading.Thread(target=send_current_containers).start()

    try:
        conn = pika.BlockingConnection(pika.URLParameters(cfg.transport_url))
        channel = conn.channel()
        channel.basic_qos(prefetch_count=1)

        dockeraken_qname = f"dockeraken-{cfg.dockeraken_id}"

        channel.queue_declare(dockeraken_qname)
        channel.exchange_declare(exchname.control_signal,
                                 exchange_type="direct")

        channel.queue_bind(dockeraken_qname, exchname.control_signal,
                           cfg.dockeraken_id)
        channel.basic_consume(dockeraken_qname,
                              on_message_callback=callback,
                              auto_ack=False)
        logging.info(" [*] Waiting for control. To exit press CTRL+C")
        channel.start_consuming()

    except KeyboardInterrupt:
        stop = True
        logging.info("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
