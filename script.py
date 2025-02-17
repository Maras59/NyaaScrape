from utils import harvest_magnet_links, start_qBit
import yaml

YAML_PATH = 'config.yaml'

with open(YAML_PATH) as stream:
    try:
        conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        exit(exc)

magnet_links = harvest_magnet_links(conf=conf)

start_qBit(magnet_links, conf=conf)
