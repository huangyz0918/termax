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
        prompt = (
            f"Provide only shell commands for os without any description. "
            f"If there is a lack of details, provide most logical solution. "
            f"Ensure the output is a valid shell command. "
            f"If multiple steps required try to combine them together using combine. "
            f"Provide only plain text without Markdown formatting. "
            f"Do not provide markdown formatting such as ```. \n\n"
            f"Here are System & User Info: \n"
            f"Operating system: {self.os} \n"
            f"Current working directory: {self.cwd} \n"
            f"Files in directory: {self.files} \n"
            f"Computer architecture: {self.architecture} \n"
            f"User environment variables: {self.environ}"
        )

        return prompt
