import importlib, warnings

from .types import Model
from termax.prompt import extract_shell_commands


class ClaudeModel(Model):
    def __init__(self, api_key, version, prompt, generation_config):
        spec = importlib.util.find_spec("anthropic")
        if spec is not None:
            import anthropic
        else:
            warnings.warn(
                "It seems you didn't install anthropic. In order to enable the Anthropic client related features, "
                "please make sure anthropic Python package has been installed. "
                "More information, please refer to: https://www.anthropic.com/api"
            )
            exit(1)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.version = version
        self.prompt = prompt
        self.generation_config = generation_config

    def to_command(self, request):
        message = self.client.messages.create(
            model=self.version,
            system=self.prompt,
            max_tokens=self.generation_config['max_tokens'],
            temperature=self.generation_config['temperature'],
            top_k=self.generation_config['top_k'],
            top_p=self.generation_config['top_p'],
            stop_sequences=self.generation_config['stop_sequences'],
            messages=[{"role": "user", "content": request}]
        )
        response = message.content[0].text
        return extract_shell_commands(response)
    
    def to_description(self, command):
        message = self.client.messages.create(
            model=self.version,
            max_tokens=self.generation_config['max_tokens'],
            temperature=self.generation_config['temperature'],
            top_k=self.generation_config['top_k'],
            top_p=self.generation_config['top_p'],
            stop_sequences=self.generation_config['stop_sequences'],
            messages=[{"role": "user", "content": f"Help me describe this command: {command}"}]
        )
        response = message.content[0].text
        return response
