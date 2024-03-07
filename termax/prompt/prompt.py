import os
import platform

class Prompt:
    def __init__(self):
        self.os = f'{platform.system()} {platform.release()}'
        self.cwd = os.getcwd()
        self.environ = os.environ
        self.architecture = platform.platform()
        self.files = os.listdir('.')
    
    def produce(self, request):
        prompt = f"Provide only shell commands for os without any description. \
        If there is a lack of details, provide most logical solution. \
        Ensure the output is a valid shell command. \
        If multiple steps required try to combine them together using combine. \
        Provide only plain text without Markdown formatting. \
        Do not provide markdown formatting such as ``` \
        System & User Info: \
        Operating system: {self.os}, Current working directory: {self.cwd}, Files in directory: {self.files}, \
        Computer architecture: {self.architecture}, User environment variables: {self.environ}"
        
        return prompt