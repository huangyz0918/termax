from openai import OpenAI

from .types import Model
from termax.prompt import extract_shell_commands


class OpenAIModel(Model):
    def __init__(self, api_key, version, prompt, temperature):
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
