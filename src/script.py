from utils import harvest_magnet_links, start_qBit
import yaml
import logging

CONFIG_PATH = 'configs/config.yaml'

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename='NyaaScrape.log',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

with open(CONFIG_PATH) as stream:
    try:
        conf = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        exit(exc)

logger.info('Started a magnet link harvest')

magnet_links = harvest_magnet_links(conf=conf)
start_qBit(magnet_links, conf=conf)

logger.info('Finished magnet link harvest')
