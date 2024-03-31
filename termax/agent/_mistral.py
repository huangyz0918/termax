import importlib.util

from termax.utils.const import *
from termax.prompt import extract_shell_commands
from .types import Model


class MistralModel(Model):
    def __init__(self, api_key, version, generation_config):
        """
        Initialize the Mistral model.
        Args:
            api_key (str): The Mistral API key.
            version (str): The model version.
            generation_config (dict): The generation configuration.
        """
        super().__init__()

        dependency = "mistralai"
        spec = importlib.util.find_spec(dependency)
        if spec is not None:
            self.MistralClient = importlib.import_module("mistralai.client").MistralClient
            self.ChatMessage = importlib.import_module("mistralai.models.chat_completion").ChatMessage
        else:
            raise ImportError(
                "It seems you didn't install mistralai. In order to enable the Mistral client related features, "
                "please make sure the mistralai Python package has been installed. "
                "More information, please refer to: https://docs.mistral.ai/api/"
            )

        self.version = version
        self.model_type = CONFIG_SEC_MISTRAL
        self.client = self.MistralClient(api_key=api_key)
        self.generation_config = generation_config

    def guess_command(self, history, prompt):
        """
        Guess the command based on the prompt.
        Args:
            history (str): The history.
            prompt (str): The prompt.
        """
        chat_response = self.client.chat(
            model=self.version,
            messages=[
                self.ChatMessage(role="system", content=prompt),
                self.ChatMessage(role="user", content=history)
            ],
            temperature=self.generation_config['temperature'],
            top_p=self.generation_config['top_p'],
            max_tokens=self.generation_config['max_tokens']
        )
        response = chat_response.choices[0].message.content
        return extract_shell_commands(response)

    def to_command(self, prompt, text):
        """
        Generate a command based on the prompt and text.
        Args:
            prompt (str): The prompt.
            text (str): The text.
        """
        chat_response = self.client.chat(
            model=self.version,
            messages=[
                self.ChatMessage(role="system", content=prompt),
                self.ChatMessage(role="user", content=text)
            ],
            temperature=self.generation_config['temperature'],
            top_p=self.generation_config['top_p'],
            max_tokens=self.generation_config['max_tokens']
        )
        response = chat_response.choices[0].message.content
        return extract_shell_commands(response)

    def to_description(self, prompt, command):
        """
        Generate a description based on the prompt and command.
        Args:
            prompt (str): The prompt.
            command (str): The command.
        """
        chat_response = self.client.chat(
            model=self.version,
            messages=[self.ChatMessage(role="user", content=f"{prompt} {command}")],
            temperature=self.generation_config['temperature'],
            top_p=self.generation_config['top_p'],
            max_tokens=self.generation_config['max_tokens']
        )
        return chat_response.choices[0].message.content
