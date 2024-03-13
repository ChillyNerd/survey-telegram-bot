import datetime
import logging
import logging.handlers
import os
from typing import Optional

import yaml


class Config:
    token: str = None
    proxy_host: str = None
    proxy_port: str = None
    proxy_user: str = None
    proxy_pass: str = None
    proxy_protocol: str = 'http'
    logging_level: str = logging.INFO
    config_file: dict = None

    def __init__(self, config_path: str = os.path.join(os.getcwd(), 'config.yaml')):
        if config_path is not None and os.path.exists(config_path):
            with open(config_path, encoding='utf-8') as file:
                self.config_file = yaml.load(file, Loader=yaml.FullLoader)
                self.set_config_parameter('token', str, 'bot', 'token')
                self.set_config_parameter('proxy_host', str, 'proxy', 'host')
                self.set_config_parameter('proxy_port', str, 'proxy', 'port')
                self.set_config_parameter('proxy_user', str, 'proxy', 'user')
                self.set_config_parameter('proxy_pass', str, 'proxy', 'pass')
                self.set_config_parameter('proxy_protocol', str, 'proxy', 'protocol')
                self.set_config_parameter('logging_level', str, 'log', 'level')
        self.config_logging()

    def config_logging(self):
        current_date = str(datetime.datetime.now().date())
        logs_path = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(logs_path):
            os.mkdir(logs_path)
        handler = logging.handlers.RotatingFileHandler(os.path.join(logs_path, f'{current_date}.log'), mode='a',
                                                       maxBytes=5_000_000, backupCount=1000)
        logger_handlers = [handler, logging.StreamHandler()]
        logging.basicConfig(format='%(asctime)s - %(name)25s %(levelname)-10s %(threadName)20s: %(message)s',
                            handlers=logger_handlers, level=logging.getLevelName(self.logging_level))
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

    def set_config_parameter(self, config_parameter, parameter_type: type, *parameter_names):
        if len(parameter_names) == 0:
            return
        inner_config = self.config_file
        for parameter_name in parameter_names:
            if not isinstance(inner_config, dict) or parameter_name not in inner_config.keys():
                return
            inner_config = inner_config[parameter_name]
        if not isinstance(inner_config, dict):
            self.__setattr__(config_parameter, parameter_type(inner_config))

    @property
    def proxy(self) -> Optional[str]:
        if self.proxy_host is None or self.proxy_port is None:
            return None
        host_token = f'{self.proxy_host}:{self.proxy_port}'
        if self.proxy_user is None or self.proxy_pass is None:
            return f'{self.proxy_protocol}://{host_token}'
        return f'{self.proxy_protocol}://{self.proxy_user}:{self.proxy_pass}@{host_token}'
