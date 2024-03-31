import importlib.util

from .types import Model
from termax.utils.const import *
from termax.prompt import extract_shell_commands


class ClaudeModel(Model):
    def __init__(self, api_key, version, generation_config):
        """
        Initialize the Claude model.
        Args:
            api_key (str): The Claude API key.
            version (str): The model version.
            generation_config (dict): The generation configuration.
        """
        super().__init__()
        dependency = "anthropic"
        spec = importlib.util.find_spec(dependency)
        if spec is not None:
            self.anthropic = importlib.import_module(dependency)
        else:
            raise ImportError(
                "It seems you didn't install anthropic. In order to enable the Anthropic client related features, "
                "please make sure anthropic Python package has been installed. "
                "More information, please refer to: https://www.anthropic.com/api"
            )

        self.version = version
        self.model_type = CONFIG_SEC_CLAUDE
        self.client = self.anthropic.Anthropic(api_key=api_key)
        self.generation_config = generation_config

    def guess_command(self, history, prompt):
        """
        Guess the command based on the prompt.
        """
        message = self.client.messages.create(
            model=self.version,
            system=prompt,
            max_tokens=self.generation_config['max_tokens'],
            temperature=self.generation_config['temperature'],
            top_k=self.generation_config['top_k'],
            top_p=self.generation_config['top_p'],
            stop_sequences=self.generation_config['stop_sequences'],
            messages=[{"role": "user", "content": history}]
        )
        response = message.content[0].text
        return extract_shell_commands(response)

    def to_command(self, prompt, text):
        """
        Generate a command based on the prompt and text.
        Args:
            prompt (str): The prompt.
            text (str): The text.
        """
        message = self.client.messages.create(
            model=self.version,
            system=prompt,
            max_tokens=self.generation_config['max_tokens'],
            temperature=self.generation_config['temperature'],
            top_k=self.generation_config['top_k'],
            top_p=self.generation_config['top_p'],
            stop_sequences=self.generation_config['stop_sequences'],
            messages=[{"role": "user", "content": text}]
        )
        response = message.content[0].text
        return extract_shell_commands(response)

    def to_description(self, prompt, command):
        """
        Generate a description based on the prompt and command.
        Args:
            prompt (str): The prompt.
            command (str): The command.
        """
        message = self.client.messages.create(
            model=self.version,
            max_tokens=self.generation_config['max_tokens'],
            temperature=self.generation_config['temperature'],
            top_k=self.generation_config['top_k'],
            top_p=self.generation_config['top_p'],
            stop_sequences=self.generation_config['stop_sequences'],
            messages=[{"role": "user", "content": f"{prompt} {command}"}]
        )
        response = message.content[0].text
        return response
