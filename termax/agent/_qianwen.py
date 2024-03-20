import importlib, warnings

from .types import Model
from termax.prompt import extract_shell_commands


class QianWenModel(Model):
    def __init__(self, api_key, version, prompt, generation_config):
        spec = importlib.util.find_spec("dashscope")
        if spec is not None:
            import dashscope
        else:
            warnings.warn(
                "It seems you didn't install dashscope. In order to enable the QianWen client related features, "
                "please make sure dashscope Python package has been installed. "
                "More information, please refer to: https://help.aliyun.com/zh/dashscope/developer-reference/api-details"
            )
            exit(1)
        dashscope.api_key = api_key
        self.version = version
        self.chat_history = [{'role': 'system', 'content': prompt},
                             {'role': 'user', 'content': None}]
        self.generation_config = generation_config

    def to_command(self, request):
        self.chat_history[1]['content'] = request
        message = dashscope.Generation.call(
            model=self.version,
            messages=self.chat_history,
            max_tokens=self.generation_config['max_tokens'],
            temperature=self.generation_config['temperature'],
            top_k=self.generation_config['top_k'],
            top_p=self.generation_config['top_p'],
            stop=self.generation_config['stop'],
        )
        response = message['output'].text
        return extract_shell_commands(response)
