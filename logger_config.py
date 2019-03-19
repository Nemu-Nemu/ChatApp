import logging
import logging.config
import yaml
import os

app_path = os.path.dirname(os.path.realpath(__file__))

with open('{}/config.yml'.format(app_path), 'r') as file:
    config = yaml.load(file)
    logging.config.dictConfig(config)
