import importlib.util

from .types import Model
from termax.prompt import extract_shell_commands


class OpenAIModel(Model):
    def __init__(self, api_key, version, temperature):
        """
        Initialize the OpenAI model.
        Args:
            api_key (str): The OpenAI API key.
            version (str): The model version.
            temperature (float): The temperature value.
        """
        super().__init__()

        dependency = "openai"
        spec = importlib.util.find_spec(dependency)
        if spec is not None:
            self.OpenAI = importlib.import_module(dependency).OpenAI
        else:
            raise ImportError(
                "It seems you didn't install openai. In order to enable the OpenAI client related features, "
                "please make sure openai Python package has been installed. "
                "More information, please refer to: https://openai.com/product"
            )

        self.version = version
        self.temperature = temperature
        self.client = self.OpenAI(api_key=api_key)

    def guess_command(self, prompt):
        """
        Guess the command based on the prompt.
        Args:
            prompt (str): The prompt.
        """
        completion = self.client.chat.completions.create(
            model=self.version,
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": "",
                }
            ],
            temperature=self.temperature
        )
        response = completion.choices[0].message.content
        return extract_shell_commands(response)

    def to_command(self, prompt, text):
        """
        Generate a command based on the prompt and text.
        Args:
            prompt (str): The prompt.
            text (str): The text.
        """
        chat_history = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": text,
            }
        ]

        completion = self.client.chat.completions.create(
            model=self.version,
            messages=chat_history,
            temperature=self.temperature
        )
        response = completion.choices[0].message.content
        return extract_shell_commands(response)

    def to_description(self, prompt, command):
        """
        Generate a description based on the prompt and command.
        Args:
            prompt (str): The prompt.
            command (str): The command.
        """
        completion = self.client.chat.completions.create(
            model=self.version,
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt} {command}",
                }
            ],
            temperature=self.temperature
        )
        response = completion.choices[0].message.content
        return response
