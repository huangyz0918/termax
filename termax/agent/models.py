from abc import ABC, abstractmethod
import subprocess
from openai import OpenAI


class Model(ABC):
    @abstractmethod
    def to_command(self, request):
        """
        This method should implement the logic to send a request to an API
        and return the command.
        """
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
        print(f'{response} \n')

        subprocess.run(response, shell=True, text=True)
