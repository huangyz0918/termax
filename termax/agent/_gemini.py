import importlib, warnings

from .types import Model
from termax.prompt import extract_shell_commands


class GeminiModel(Model):
    def __init__(self, api_key, version, prompt, generation_config):
        spec = importlib.util.find_spec("google.generativeai")
        if spec is not None:
            import google.generativeai as genai
            import google.ai.generativelanguage as glm
        else:
            warnings.warn(
                "It seems you didn't install google.generativeai. In order to enable the Gemini client related features, "
                "please make sure google.generativeai Python package has been installed. "
                "More information, please refer to: https://ai.google.dev/"
            )
            exit(1)
        self.client = genai.configure(api_key=api_key)
        self.version = version
        self.chat_history = [glm.Content(parts=[glm.Part(text=prompt)], role="user"),
                             glm.Content(parts=[glm.Part(text="understand")], role="model")]
        self.generation_config = genai.GenerationConfig(
            stop_sequences=generation_config['stop_sequences'],
            temperature=generation_config['temperature'],
            top_p=generation_config['top_p'],
            top_k=generation_config['top_k'],
            candidate_count=generation_config['candidate_count'],
            max_output_tokens=generation_config['max_output_tokens'])

    def to_command(self, request):
        model = genai.GenerativeModel(self.version)
        chat = model.start_chat(history=self.chat_history)
        response = chat.send_message(request, generation_config=self.generation_config).text
        return extract_shell_commands(response)
