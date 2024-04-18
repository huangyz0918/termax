import json
import importlib.util

from .types import Model
from termax.prompt import extract_shell_commands, is_url
from termax.function import get_all_function_schemas, get_all_functions


class OllamaModel(Model):
    def __init__(self, host_url, version):
        """
        Initialize the Ollama model.
        Args:
            host_url (str): The Ollama Host url.
            version (str): The model version.
            temperature (float): The temperature value.
        """
        super().__init__()

        dependency = "ollama"
        spec = importlib.util.find_spec(dependency)
        if spec is not None:
            self.ollama = importlib.import_module(dependency)
            self.Client = importlib.import_module(dependency).Client
            self.ResponseError = importlib.import_module(dependency).ResponseError
        else:
            raise ImportError(
                "It seems you didn't install ollama. In order to enable the Ollama client related features, "
                "please make sure ollama Python package has been installed. "
                "More information, please refer to: https://github.com/ollama/ollama-python"
            )

        self.version = version
        if is_url(host_url):
            self.client = self.Client(host=host_url)
        else:
            self.client = self.Client()

    def guess_command(self, history, prompt):
        """
        Guess the command based on the prompt.
        Args:
            history (str): The history.
            prompt (str): The prompt.
        """
        try:
            chat_history = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": history}
            ]

            completion = self.client.chat(
                model=self.version,
                messages=chat_history,
            )

            response = completion['message']['content']
            return extract_shell_commands(response)
        except self.ResponseError as e:
            print(f"Ollama Error: {e.error}")
        except Exception as e:
            print("Ollama error occurred.")
            print(f"Error message: {e}")

    def to_command(self, prompt, text):
        """
        Generate a command based on the prompt and text.
        Args:
            prompt (str): The prompt.
            text (str): The text.
        """
        try:
            chat_history = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ]
            
            completion = self.client.chat(
                model=self.version,
                messages=chat_history,
            )

            response = completion['message']['content']
            return extract_shell_commands(response)
        except self.ResponseError as e:
            print(f"Ollama Error: {e.error}")
        except Exception as e:
            print("Ollama error occurred.")
            print(f"Error message: {e}")

    def to_description(self, prompt, command):
        """
        Generate a description based on the prompt and command.
        Args:
            prompt (str): The prompt.
            command (str): The command.
        """
        try:
            chat_history = [
                {"role": "user", "content": f"{prompt} {command}"},
            ]

            completion = self.client.chat(
                model=self.version,
                messages=chat_history,
            )

            response = completion['message']['content']
            return response
        except self.ResponseError as e:
            print(f"Ollama Error: {e.error}")
        except Exception as e:
            print("Ollama error occurred.")
            print(f"Error message: {e}")
