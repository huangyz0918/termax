import subprocess
from openai import OpenAI
from abc import ABC, abstractmethod

from termax.prompt import extract_shell_commands


class Model(ABC):
    @abstractmethod
    def to_command(self, request):
        pass


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
        command = extract_shell_commands(response)
        print(f'{command}')

        subprocess.run(command, shell=True, text=True)
