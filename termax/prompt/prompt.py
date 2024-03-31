from .memory import Memory
from termax.utils.metadata import *
from termax.utils import CONFIG_SEC_OPENAI

from datetime import datetime


class Prompt:
    def __init__(self, memory):
        """
        Prompt for Termax: the prompt for the LLMs.
        Args:
            memory: the memory instance.
        """
        # TODO: make the sync of system related metadata once happened at the initialization
        self.system_metadata = get_system_metadata()
        self.path_metadata = get_path_metadata()
        self.command_history = get_command_history()

        # share the same memory instance.
        if memory is None:
            self.memory = Memory()
        else:
            self.memory = memory

    def gen_suggestions(self, ref_num: int = 10, model: str = CONFIG_SEC_OPENAI):
        """
        [Prompt] Generate the suggestions based on the environment and the history.
        Args:
            ref_num: the number of the references to use.
            model: the model to use, default is OpenAI.
        """

        history = get_command_history(ref_num)['shell_command_history']
        history_string = ""
        for i in history:
            if i['command'] == "t guess" or i['command'] == "termax guess":
                continue

            history_string += f"""
            Command: {i['command']}
            Date: {i['time']}\n
            """

        files = get_file_metadata()
        if model == CONFIG_SEC_OPENAI:
            return f"""
            You are an shell expert, you need to guess the next command based on the information provided.\n
            
            [INFORMATION] The user's current system information:\n
            
            1. OS: {self.system_metadata['platform']}
            2. OS Version: {self.system_metadata['platform_version']}
            3. Architecture: {self.system_metadata['architecture']}
            
            [INFORMATION] The user's current PATH information:\n
            
            1. User: {self.path_metadata['user']}
            2. Current PATH: {self.path_metadata['current_directory']}
            3. Files under the current directory: {files['files']}
            4. Directories under the current directory: {files['directory']}
            5. Invisible files under the current directory: {files['invisible_files']}
            6. Invisible directories under the current directory: {files['invisible_directory']}
            
            [INFORMATION] The current time: {datetime.now().isoformat()}\n
            
            Here are some rules you need to follow:\n
                        
            1. Please provide only shell commands for os without any description.
            2. Ensure the output is a valid shell command.
            
            Commands: ${{commands}}
            
            """
        else:
            return f"""
            You are an shell expert, you need to guess the next command based on the information provided.\n

            [INFORMATION] The user's current system information:\n

            1. OS: {self.system_metadata['platform']}
            2. OS Version: {self.system_metadata['platform_version']}
            3. Architecture: {self.system_metadata['architecture']}

            [INFORMATION] The user's current PATH information:\n

            1. User: {self.path_metadata['user']}
            2. Current PATH: {self.path_metadata['current_directory']}
            3. Files under the current directory: {files['files']}
            4. Directories under the current directory: {files['directory']}
            5. Invisible files under the current directory: {files['invisible_files']}
            6. Invisible directories under the current directory: {files['invisible_directory']}

            [INFORMATION] The current time: {datetime.now().isoformat()}\n

            Here are some rules you need to follow:\n

            1. Please provide only shell commands for os without any description.
            2. Ensure the output is a valid shell command.

           Commands: ${{commands}}

            """

    def explain_commands(self, model: str = CONFIG_SEC_OPENAI):
        """
        [Prompt] Explain the shell commands.
        Args:
            model: the model to use, default is OpenAI.
        """
        if model == CONFIG_SEC_OPENAI:
            return f"Help me describe this command:"
        else:
            # TODO: add more models specific prompt
            return f"Help me describe this command:"

    def gen_commands(self, text: str, model: str = CONFIG_SEC_OPENAI):
        """
        [Prompt] Convert the natural language text to the commands.
        Args:
            text: the natural language text.
            model: the model to use, default is OpenAI.
        """
        # query the history database to get similar samples
        samples = self.memory.query([text], n_results=5)
        metadatas = samples['metadatas'][0]
        documents = samples['documents'][0]
        distances = samples['distances'][0]

        # construct a string that contains the samples in a human-readable format
        sample_string = ""
        for i in range(len(documents)):
            sample_string += f"""
            User Input: {documents[i]}
            Generated Commands: {metadatas[i]['response']}
            Distance Score: {distances[i]}
            Date: {metadatas[i]['created_at']}\n
            """

        # refresh the metadata
        self.command_history = get_command_history()
        if model == CONFIG_SEC_OPENAI:
            return f"""
            You are an shell expert, you can convert this text to shell commands.\n
            
            1. Please provide only shell commands for os without any description.
            2. Ensure the output is a valid shell command.
            3. If multiple steps required try to combine them together.
            
            Here are some rules you need to follow:\n
            
            1. The commands should be able to run on the current system according to the system information.
            2. The files in the commands (if any) should be available in the path, according to the path information.
            3. The CLI application should be installed in the system (check the path information).
            
            Here are some information you may need to know:\n
            
            \nCurrent system information (in dict format): {self.system_metadata} \n
            
            \nThe user's system PATH information (in dict format): {self.path_metadata} \n
            
            \nThe user's command history (in dict format): {self.command_history} \n
            
            Here are some similar commands generated before:\n
            
            {sample_string}
            
            The output shell commands is (please replace the `{{commands}}` with the actual commands):
            
            Commands: ${{commands}}
            """
        else:
            # TODO: add more models specific prompt
            return f"""
            You are an shell expert, you can convert this text to shell commands.\n

            1. Please provide only shell commands for os without any description.
            2. Ensure the output is a valid shell command.
            3. If multiple steps required try to combine them together.

            Here are some rules you need to follow:\n

            1. The commands should be able to run on the current system according to the system information.
            2. The files in the commands (if any) should be available in the path, according to the path information.
            3. The CLI application should be installed in the system (check the path information).

            Here are some information you may need to know:\n

            \nCurrent system information (in dict format): {self.system_metadata} \n

            \nThe user's system PATH information (in dict format): {self.path_metadata} \n

            \nThe user's command history (in dict format): {self.command_history} \n

            Here are some similar commands generated before:\n

            {sample_string}

            The output shell commands is (please replace the `{{commands}}` with the actual commands):

            Commands: ${{commands}}
            """
