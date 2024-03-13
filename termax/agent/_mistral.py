from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from .types import Model
from termax.prompt import extract_shell_commands


class MistralModel(Model):
    def __init__(self, api_key, version, prompt, generation_config):
        self.client = MistralClient(api_key=api_key)
        self.version = version
        self.chat_history = [ChatMessage(role="system", content=prompt)]
        self.generation_config = generation_config

    def to_command(self, request):
        self.chat_history.append(ChatMessage(role="user", content=request))
        chat_response = self.client.chat(
            model=self.version,
            messages=self.chat_history,
            temperature=self.generation_config['temperature'],
            top_p=self.generation_config['top_p'],
            max_tokens=self.generation_config['max_tokens']
        )
        response = chat_response.choices[0].message.content
        return extract_shell_commands(response)
