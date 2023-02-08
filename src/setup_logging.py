import logging.config
import yaml

# setup logging module
with open(os.path.abspath(os.path.join("src", "logging.yaml")), "r") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
