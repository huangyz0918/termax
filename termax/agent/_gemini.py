import importlib.util

from .types import Model
from termax.utils.const import *
from termax.prompt import extract_shell_commands


class GeminiModel(Model):
    def __init__(self, api_key, version, generation_config):
        """
        Initialize the Gemini model.
        Args:
            api_key (str): The Gemini API key.
            version (str): The model version.
            generation_config (dict): The generation configuration.
        """
        super().__init__()
        dependency = "google.generativeai"
        spec = importlib.util.find_spec(dependency)
        if spec is not None:
            self.genai = importlib.import_module(dependency)
            self.glm = importlib.import_module("google.ai.generativelanguage")
        else:
            raise ImportError(
                "It seems you didn't install google.generativeai. "
                "In order to enable the Gemini client related features, "
                "please make sure google.generativeai Python package has been installed. "
                "More information, please refer to: https://ai.google.dev/"
            )

        self.version = version
        self.model_type = CONFIG_SEC_GEMINI
        self.client = self.genai.configure(api_key=api_key)
        self.generation_config = self.genai.GenerationConfig(
            stop_sequences=generation_config['stop_sequences'],
            temperature=generation_config['temperature'],
            top_p=generation_config['top_p'],
            top_k=generation_config['top_k'],
            candidate_count=generation_config['candidate_count'],
            max_output_tokens=generation_config['max_output_tokens'])

    def to_command(self, prompt, text):
        """
        Generate a command based on the prompt and text.
        Args:
            prompt (str): The prompt.
            text (str): The text.
        """
        chat_history = [
            self.glm.Content(parts=[self.glm.Part(text=prompt)], role="user"),
            self.glm.Content(parts=[self.glm.Part(text="understand")], role="model")
        ]

        model = self.genai.GenerativeModel(self.version)
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(text, generation_config=self.generation_config).text
        return extract_shell_commands(response)

    def to_description(self, prompt, command):
        """
        Generate a description based on the prompt and command.
        Args:
            prompt (str): The prompt.
            command (str): The command.

        """
        model = self.genai.GenerativeModel(self.version)
        chat = model.start_chat(history=[])
        response = chat.send_message(f"{prompt} {command}", generation_config=self.generation_config).text
        return response
