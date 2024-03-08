from openai import OpenAI
import google.generativeai as genai
import google.ai.generativelanguage as glm
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
        return extract_shell_commands(response)
        

class GeminiModel(Model):
    def __init__(self, api_key, version, prompt, generation_config):
        self.client = genai.configure(api_key=api_key)
        self.version = version
        self.chat_history = [glm.Content(parts=[glm.Part(text=prompt)], role="user"), glm.Content(parts=[glm.Part(text="understand")], role="model")]
        self.generation_config = genai.GenerationConfig(
            stop_sequences = generation_config['stop_sequences'],
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

