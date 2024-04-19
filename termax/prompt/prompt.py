from .memory import Memory
from termax.utils.metadata import *
from termax.utils import CONFIG_SEC_OPENAI

import textwrap
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

    def intent_detect(self, model: str = CONFIG_SEC_OPENAI):
        """
        [Prompt] Detect the intent of code type based on the command history.
        Args:
            model: the model to use, default is OpenAI.
        """
        files = get_file_metadata()
        if model == CONFIG_SEC_OPENAI:
            return textwrap.dedent(
                f"""\
                Analyze the provided list of command history entries and infer the primary command or tool being
                utilized based on the pattern, context, and sequence of these commands.
                The term "primary command" refers to the main or leading command in a sequence
                of operations or instructions.

                [INFORMATION] The user's current system information:
                
                1. OS: {self.system_metadata['platform']}
                2. OS Version: {self.system_metadata['platform_version']}
                3. Architecture: {self.system_metadata['architecture']}
                
                [INFORMATION] The user's current PATH information:
                
                1. User: {self.path_metadata['user']}
                2. Current PATH: {self.path_metadata['current_directory']}
                3. Files under the current directory: {files['files']}
                4. Directories under the current directory: {files['directory']}
                5. Invisible files under the current directory: {files['invisible_files']}
                6. Invisible directories under the current directory: {files['invisible_directory']}

                [INFORMATION] The current time: {datetime.now().isoformat()}

                Here are some rules you need to follow:
                1. Don't include Subcommand/Argument in the output.
                
                The output shell primary command is (please replace the `{{primary_command}}` with the primary command):
                
                Command: ${{primary_command}}
                """
            )
        else:
            # TODO: add more models specific prompt
            return textwrap.dedent(
                f"""\
                Analyze the provided list of command history entries and infer the primary command or tool being
                utilized based on the pattern, context, and sequence of these commands.
                The term "primary command" refers to the main or leading command in a sequence of
                operations or instructions.
                
                [INFORMATION] The user's current system information:
                
                1. OS: {self.system_metadata['platform']}
                2. OS Version: {self.system_metadata['platform_version']}
                3. Architecture: {self.system_metadata['architecture']}
                
                [INFORMATION] The user's current PATH information:
                
                1. User: {self.path_metadata['user']}
                2. Current PATH: {self.path_metadata['current_directory']}
                3. Files under the current directory: {files['files']}
                4. Directories under the current directory: {files['directory']}
                5. Invisible files under the current directory: {files['invisible_files']}
                6. Invisible directories under the current directory: {files['invisible_directory']}
                
                [INFORMATION] The current time: {datetime.now().isoformat()}

                Here are some rules you need to follow:
                1. Don't include Subcommand/Argument in the output.
                
                The output shell primary command is (please replace the `{{primary_command}}` with the primary command):
                
                Command: ${{primary_command}}
                """
            )

    def gen_suggestions(self, primary: str, model: str = CONFIG_SEC_OPENAI):
        """
        [Prompt] Generate the suggestions based on the environment and the history.
        Args:
            primary: the primary data source, could be git or docker.
            model: the model to use, default is OpenAI.
        """
        if primary == 'git':
            primary_data = "\n".join(
                f"{index + 1}. {key}: {value}" for index, (key, value) in enumerate(get_git_metadata().items()))
        elif primary == 'docker':
            primary_data = "\n".join(
                f"{index + 1}. {key}: {value}" for index, (key, value) in enumerate(get_docker_metadata().items()))
        else:
            primary_data = 'None'

        files = get_file_metadata()
        if model == CONFIG_SEC_OPENAI:
            return textwrap.dedent(
                f"""\
                You are an shell expert, you need to infer the next command based on the provided list
                of command history entries.
                
                [INFORMATION] The user's current system information:
                
                1. OS: {self.system_metadata['platform']}
                2. OS Version: {self.system_metadata['platform_version']}
                3. Architecture: {self.system_metadata['architecture']}
                
                [INFORMATION] The user's current PATH information:

                1. User: {self.path_metadata['user']}
                2. Current PATH: {self.path_metadata['current_directory']}
                3. Files under the current directory: {files['files']}
                4. Directories under the current directory: {files['directory']}
                5. Invisible files under the current directory: {files['invisible_files']}
                6. Invisible directories under the current directory: {files['invisible_directory']}
                
                [INFORMATION] The current time: {datetime.now().isoformat()}

                [INFORMATION] The primary command information:
                {primary_data}
                
                Here are some rules you need to follow:
                1. Please provide only shell commands for os without any description.
                2. Ensure the output is a valid shell command.
                
                The output shell commands is (please replace the `{{commands}}` with the actual commands):

                Commands: ${{commands}}
                """
            )
        else:
            # TODO: add more models specific prompt
            return textwrap.dedent(
                f"""\
                You are an shell expert, you need to infer the next command based on the provided list of
                command history entries.
                
                [INFORMATION] The user's current system information:
                
                1. OS: {self.system_metadata['platform']}
                2. OS Version: {self.system_metadata['platform_version']}
                3. Architecture: {self.system_metadata['architecture']}
                
                [INFORMATION] The user's current PATH information:

                1. User: {self.path_metadata['user']}
                2. Current PATH: {self.path_metadata['current_directory']}
                3. Files under the current directory: {files['files']}
                4. Directories under the current directory: {files['directory']}
                5. Invisible files under the current directory: {files['invisible_files']}
                6. Invisible directories under the current directory: {files['invisible_directory']}

                [INFORMATION] The current time: {datetime.now().isoformat()}
                
                [INFORMATION] The primary command information:
                {primary_data}
                
                Here are some rules you need to follow:
                1. Please provide only shell commands for os without any description.
                2. Ensure the output is a valid shell command.
                
                The output shell commands is (please replace the `{{commands}}` with the actual commands):
                
                Commands: ${{commands}}
                """
            )

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
        samples = self.memory.query([text])
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
        files = get_file_metadata()
        if model == CONFIG_SEC_OPENAI:
            return textwrap.dedent(
                f"""\
                You are an shell expert, you can convert natural language text from user to shell commands.
                
                1. Please provide only shell commands for os without any description.
                2. Ensure the output is a valid shell command.
                3. If multiple steps required try to combine them together.
                
                Here are some rules you need to follow:

                1. The commands should be able to run on the current system according to the system information.
                2. The files in the commands should be available in the path, according to the path information.
                3. The CLI application should be installed in the system (check the path information).

                Here are some information you may need to know:
                
                [INFORMATION] The user's current system information:
                1. OS: {self.system_metadata['platform']}
                2. OS Version: {self.system_metadata['platform_version']}
                3. Architecture: {self.system_metadata['architecture']}
                
                [INFORMATION] The user's current PATH information:
                1. User: {self.path_metadata['user']}
                2. Current PATH: {self.path_metadata['current_directory']}
                3. Files under the current directory: {files['files']}
                4. Directories under the current directory: {files['directory']}
                5. Invisible files under the current directory: {files['invisible_files']}
                6. Invisible directories under the current directory: {files['invisible_directory']}
    
                Here are some similar commands generated before:
                {sample_string}

                The output shell commands is (please replace the `{{commands}}` with the actual commands):

                Commands: ${{commands}}
                """
            )
        else:
            # TODO: add more models specific prompt
            return textwrap.dedent(
                f"""\
                You are an shell expert, you can convert natural language text from user to shell commands.
                
                1. Please provide only shell commands for os without any extra description.
                2. Ensure the output is a valid shell command.
                3. If multiple steps required try to combine them together.
                
                Here are some rules you need to follow:

                1. The commands should be able to run on the current system according to the system information.
                2. The files in the commands should be available in the path, according to the path information.
                3. The CLI application should be installed in the system (check the path information).

                Here are some information you may need to know:
                
                [INFORMATION] The user's current system information:
                1. OS: {self.system_metadata['platform']}
                2. OS Version: {self.system_metadata['platform_version']}
                3. Architecture: {self.system_metadata['architecture']}
                
                [INFORMATION] The user's current PATH information:
                1. User: {self.path_metadata['user']}
                2. Current PATH: {self.path_metadata['current_directory']}
                3. Files under the current directory: {files['files']}
                4. Directories under the current directory: {files['directory']}
                5. Invisible files under the current directory: {files['invisible_files']}
                6. Invisible directories under the current directory: {files['invisible_directory']}
                
                Here are some similar commands generated before:
                {sample_string}
                
                The output shell commands is (please replace the `{{commands}}` with the actual commands):

                Commands: ${{commands}}
                """
            )
