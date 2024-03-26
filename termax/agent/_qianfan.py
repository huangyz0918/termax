import importlib.util

from .types import Model
from termax.prompt import extract_shell_commands


class QianFanModel(Model):
    def __init__(self, api_key, secret_key, version, prompt, generation_config):
        spec = importlib.util.find_spec("qianfan")
        if spec is not None:
            import qianfan
        else:
            raise ImportError(
                "It seems you didn't install qianfan. In order to enable the QianFan client related features, "
                "please make sure qianfan Python package has been installed. "
                "More information, please refer to: https://cloud.baidu.com/doc/WENXINWORKSHOP/s/flfmc9do2"
            )

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

    def to_description(self, command):
        message = self.client.do(
            model=self.version,
            messages=[{"role": "user", "content": f"Help me describe this command: {command}"}],
            temperature=self.generation_config['temperature'],
            top_p=self.generation_config['top_p'],
            max_output_tokens=self.generation_config['max_output_tokens']
        )
        response = message['body']['result']
        return response
