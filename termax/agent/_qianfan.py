import importlib.util

from .types import Model
from termax.utils.const import *
from termax.prompt import extract_shell_commands


class QianFanModel(Model):
    def __init__(self, api_key, secret_key, version, generation_config):
        """
        Initialize the QianFan model.
        Args:
            api_key (str): The QianFan API key.
            secret_key (str): The QianFan secret key.
            version (str): The model version.
            generation_config (dict): The generation configuration.
        """
        super().__init__()

        dependency = "qianfan"
        spec = importlib.util.find_spec(dependency)
        if spec is not None:
            self.qianfan = importlib.import_module(dependency)
        else:
            raise ImportError(
                "It seems you didn't install qianfan. In order to enable the QianFan client related features, "
                "please make sure qianfan Python package has been installed. "
                "More information, please refer to: https://cloud.baidu.com/doc/WENXINWORKSHOP/s/flfmc9do2"
            )

        self.model_type = CONFIG_SEC_QIANFAN
        self.client = self.qianfan.ChatCompletion(ak=api_key, sk=secret_key)
        self.version = version
        self.generation_config = generation_config

    def guess_command(self, history, prompt):
        """
        Guess the command based on the prompt.
        Args:
            history (str): The history.
            prompt (str): The prompt.
        """
        message = self.client.do(
            model=self.version,
            messages=[{"role": "user", "content": history}],
            system=prompt,
            temperature=self.generation_config['temperature'],
            top_p=self.generation_config['top_p'],
            max_output_tokens=self.generation_config['max_output_tokens']
        )
        response = message['body']['result']
        return extract_shell_commands(response)

    def to_command(self, prompt, text):
        """
        Generate a command based on the prompt and request.
        Args:
            prompt (str): The prompt.
            text (str): The request text.
        """
        message = self.client.do(
            model=self.version,
            messages=[{"role": "user", "content": text}],
            system=prompt,
            temperature=self.generation_config['temperature'],
            top_p=self.generation_config['top_p'],
            max_output_tokens=self.generation_config['max_output_tokens']
        )
        response = message['body']['result']
        return extract_shell_commands(response)

    def to_description(self, prompt, command):
        """
        Generate a description based on the prompt and command.
        Args:
            prompt (str): The prompt.
            command (str): The command.
        """
        message = self.client.do(
            model=self.version,
            messages=[{"role": "user", "content": f"{prompt} {command}"}],
            temperature=self.generation_config['temperature'],
            top_p=self.generation_config['top_p'],
            max_output_tokens=self.generation_config['max_output_tokens']
        )
        response = message['body']['result']
        return response
