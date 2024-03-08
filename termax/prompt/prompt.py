import os
import platform


class Prompt:
    def __init__(self):
        self.os = f'{platform.system()} {platform.release()}'
        self.cwd = os.getcwd()
        self.environ = os.environ
        self.architecture = platform.platform()
        self.files = os.listdir('.')

    def nl2commands(self):
        return f"""
        You are an shell expert, you can convert this text to shell commands.
        Please provide only shell commands for os without any description.
        Ensure the output is a valid shell command.
        If multiple steps required try to combine them together. 
        Do not provide markdown formatting such as ```.
        
        Here are some information you may need to know. \n
        
        Operating system: {self.os} \n
        
        Current working directory: {self.cwd} \n
        
        Files in directory: {self.files} \n
        
        Computer architecture: {self.architecture} \n
        
        User environment variables: {self.environ} \n
        """
