import uuid
import argparse

parser = argparse.ArgumentParser(prog="dockeraken-tools")

parser.add_argument("which",
                    help="Which module",
                    choices=["gen_config", "gen-config"],
                    type=str)

config_template = """[default]
dockeraken_id={id}
transport_url=amqps://username:password@rabbitmq.example.com/vhost"""


def main():
    args = parser.parse_args()
    if args.which in ["gen_config", "gen-config"]:
        print(config_template.format(id=uuid.uuid4().hex))