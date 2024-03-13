import qianfan

from .types import Model
from termax.prompt import extract_shell_commands


class QianFanModel(Model):
    def __init__(self, api_key, secret_key, version, prompt, generation_config):
        self.client = qianfan.ChatCompletion(ak=api_key, sk=secret_key)
        self.version = version
        self.prompt = prompt
        self.generation_config = generation_config

    def to_command(self, request):
        message = self.client.do(
            model=self.version,
            messages=[{"role": "user", "content": request}],
            system=self.prompt,
            temperature=self.generation_config['temperature'],
            top_p=self.generation_config['top_p'],
            max_output_tokens=self.generation_config['max_output_tokens']
        )
        response = message['body']['result']
        return extract_shell_commands(response)
