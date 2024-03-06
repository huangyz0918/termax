import os
import configparser
from pathlib import Path

from termax.utils import CONFIG_SEC_OPENAI


class Config:
    """
    Config: the overall system configuration for Termax.
    """

    def __init__(self):
        self.home = os.path.join(str(Path.home()), ".termax")
        Path(self.home).mkdir(parents=True, exist_ok=True)

        self.config_path = os.path.join(str(Path.home()), ".termax", "config")
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)
        self.snowflake_auth = None
        self.docker_auth = None

    def read(self):
        """
        read: read the configuration file.

        Returns: a dictionary of the configuration.
        """
        self.config.read(self.config_path)
        config_dict = {}

        for section in self.config.sections():
            options_dict = {option: self.config.get(section, option) for option in self.config.options(section)}
            config_dict[section] = options_dict

        return config_dict

    def reload_config(self, config_path):
        """
        reload_config: The default configuration will load ~/.termax/config, if user want to specify
        customize, the method is required.

        @param config_path: the path of new configuration file.
        """
        self.config.read(config_path)

    def load_openai_config(self):
        """
        load_openai_config: load a OpenAI configuration when required.
        """
        if self.config.has_section(CONFIG_SEC_OPENAI):
            return self.config[CONFIG_SEC_OPENAI]
        else:
            raise ValueError("there is no '[openai]' section found in the configuration file.")

    def write_platform(
            self,
            config_dict: dict,
            platform: str = CONFIG_SEC_OPENAI
    ):
        """
        write_platform: indicate and generate the platform related configuration.

        """
        # create the configuration to connect with OpenAI.
        if not self.config.has_section(CONFIG_SEC_OPENAI):
            self.config.add_section(CONFIG_SEC_OPENAI)

        self.config[platform] = config_dict

        # save the new configuration and reload.
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
            self.reload_config(self.config_path)
