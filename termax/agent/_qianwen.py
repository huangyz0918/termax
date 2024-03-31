import importlib.util

from .types import Model
from termax.utils.const import *
from termax.prompt import extract_shell_commands


class QianWenModel(Model):

    def __init__(self, api_key, version, generation_config):
        """
        Initialize the QianWen model.
        Args:
            api_key (str): The QianWen API key.
            version (str): The model version.
            generation_config (dict): The generation configuration.
        """
        super().__init__()

        dependency = "dashscope"
        spec = importlib.util.find_spec(dependency)
        if spec is not None:
            self.dashscope = importlib.import_module(dependency)
        else:
            raise ImportError(
                "It seems you didn't install dashscope. In order to enable the QianWen client related features, "
                "please make sure dashscope Python package has been installed. "
                "More information, "
                "please refer to: https://help.aliyun.com/zh/dashscope/developer-reference/api-details"
            )

        self.version = version
        self.model_type = CONFIG_SEC_QIANWEN
        self.dashscope.api_key = api_key
        self.generation_config = generation_config

    def guess_command(self, prompt):
        """
        Guess the command based on the prompt.
        """
        message = self.dashscope.Generation.call(
            model=self.version,
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=self.generation_config['max_tokens'],
            temperature=self.generation_config['temperature'],
            top_k=self.generation_config['top_k'],
            top_p=self.generation_config['top_p'],
            stop=self.generation_config['stop'],
        )
        response = message['output'].text
        return extract_shell_commands(response)

    def to_command(self, prompt, text):
        """
        Generate a command based on the prompt and text.
        Args:
            prompt (str): The prompt.
            text (str): The text.
        """
        chat_history = [
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': text}
        ]

        message = self.dashscope.Generation.call(
            model=self.version,
            messages=chat_history,
            max_tokens=self.generation_config['max_tokens'],
            temperature=self.generation_config['temperature'],
            top_k=self.generation_config['top_k'],
            top_p=self.generation_config['top_p'],
            stop=self.generation_config['stop'],
        )
        response = message['output'].text
        return extract_shell_commands(response)

    def to_description(self, prompt, command):
        """
        Generate a description based on the prompt and command.
        Args:
            prompt (str): The prompt.
            command (str): The command.
        """
        message = self.dashscope.Generation.call(
            model=self.version,
            messages=[{'role': 'user', 'content': f"{prompt} {command}"}],
            max_tokens=self.generation_config['max_tokens'],
            temperature=self.generation_config['temperature'],
            top_k=self.generation_config['top_k'],
            top_p=self.generation_config['top_p'],
            stop=self.generation_config['stop'],
        )
        response = message['output'].text
        return response
