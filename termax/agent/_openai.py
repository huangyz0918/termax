import importlib.util

from .types import Model
from termax.prompt import extract_shell_commands


class OpenAIModel(Model):
    def __init__(self, api_key, version, prompt, temperature):
        spec = importlib.util.find_spec("openai")
        if spec is not None:
            from openai import OpenAI
        else:
            raise ImportError(
                "It seems you didn't install openai. In order to enable the OpenAI client related features, "
                "please make sure openai Python package has been installed. "
                "More information, please refer to: https://openai.com/product"
            )

        self.client = OpenAI(api_key=api_key)
        self.version = version
        self.chat_history = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": None,
            }
        ]
        self.temperature = temperature

    def to_command(self, request):
        self.chat_history[1]['content'] = request
        completion = self.client.chat.completions.create(
            model=self.version,
            messages=self.chat_history,
            temperature=self.temperature
        )
        response = completion.choices[0].message.content
        return extract_shell_commands(response)

    def to_description(self, command):
        completion = self.client.chat.completions.create(
            model=self.version,
            messages=[
                {
                    "role": "user",
                    "content": f"Help me describe this command: {command}",
                }
            ],
            temperature=self.temperature
        )
        response = completion.choices[0].message.content
        return response
