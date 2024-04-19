import re
import os
import sys
import psutil
import socket
import shutil
import getpass
import platform
import subprocess
from datetime import datetime


def get_git_metadata():
    """
    get_git_metadata: Records the git information on the current workspace.
    Returns: a dictionary of git metadata.

    """

    def run_git_command(command):
        """
        Run a git command and return the output.
        Args:
            command: the git command to run.

        Returns: the output of the git command.

        """
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        if result.returncode != 0:
            raise Exception(f"Git command failed: {result.stderr}")
        return result.stdout.strip()

    # Check whether the directory is initialized with git
    if run_git_command("[ -d .git ] && echo 1 || echo 0") == "0":
        return {
            "git_sha": "",
            "git_current_branch": "",
            "git_remotes": [],
            "git_latest_commit_author": "",
            "git_latest_commit_date": "",
            "git_latest_commit_message": ""
        }

    # Get latest commit hash
    latest_commit_hash = run_git_command("git rev-parse HEAD")
    latest_commit_author = run_git_command("git log -1 --pretty=%an")
    latest_commit_message = run_git_command("git log -1 --pretty=%B")
    latest_commit_timestamp = run_git_command("git log -1 --pretty=%ct")
    latest_commit_date = datetime.utcfromtimestamp(int(latest_commit_timestamp)).strftime('%Y-%m-%d %H:%M:%S UTC')

    # Get current branch name
    current_branch = run_git_command("git rev-parse --abbrev-ref HEAD")

    # Get remotes
    remotes_raw = run_git_command("git remote -v")
    remotes = {}
    for line in remotes_raw.split('\n'):
        if line:
            name, url, typ = line.split()
            if name not in remotes:
                remotes[name] = {'fetchUrl': '', 'pushUrl': ''}
            if typ == '(fetch)':
                remotes[name]['fetchUrl'] = url
            elif typ == '(push)':
                remotes[name]['pushUrl'] = url

    remote_list = []
    for name, urls in remotes.items():
        remote_list.append(
            {
                "remote_name": name,
                "fetch_url": urls['fetchUrl'],
                "push_url": urls['pushUrl']
            }
        )

    return {
        "git_sha": latest_commit_hash,
        "git_current_branch": current_branch,
        "git_remotes": remote_list,
        "git_latest_commit_author": latest_commit_author,
        "git_latest_commit_date": latest_commit_date,
        "git_latest_commit_message": latest_commit_message
    }


def get_docker_metadata():
    """
    Records the Docker containers and images information of the current workspace.
    
    Returns:
        A dictionary with Docker containers and images metadata.
    """

    def parse_docker_output(output, headers):
        """
        Parses the output of a Docker command into a list of dictionaries based on provided headers.
        
        Args:
            output: String output from Docker command.
            headers: List of headers that correspond to Docker output columns.
            
        Returns:
            List of dictionaries with Docker data.
        """
        entries = []
        for line in output.strip().split('\n')[1:]:
            parts = re.split(r'\s{2,}', line)
            entry = {header: parts[i] if i < len(parts) else "" for i, header in enumerate(headers)}
            entries.append(entry)
        return entries

    def run_command(command):
        """
        Executes a shell command and returns the output.
        
        Args:
            command: List of command arguments.
        
        Returns:
            A tuple of (success flag, output or error message).
        """
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception("Docker command failed: " + e.stderr)

    containers_info = run_command(
        [
            "docker", "ps", "-a", "--format",
            "table {{.ID}}\t{{.Image}}\t{{.Command}}\t{{.CreatedAt}}\t{{.Status}}\t{{.Names}}\t{{.Ports}}"
        ]
    )
    containers_headers = ['CONTAINER ID', 'IMAGE', 'COMMAND', 'CREATED', 'STATUS', 'NAMES', 'PORTS']
    containers = parse_docker_output(containers_info, containers_headers)

    images_info = run_command(["docker", "images"])
    images_headers = ['REPOSITORY', 'TAG', 'IMAGE ID', 'CREATED', 'SIZE']
    images = parse_docker_output(images_info, images_headers)

    # docker_info = run_command(["docker", "info"])
    # docker_headers = []
    # docker = parse_docker_output(docker_info, docker_headers)

    return {
        # "docker_info": docker_info,
        "docker_containers": containers,
        "docker_images": images,
    }


def get_system_metadata():
    """
    Records the system information.

    Return a dictionary containing the system metadata.
    """
    return {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'hostname': socket.gethostname(),
        'ip_address': socket.gethostbyname(socket.gethostname()),
        'physical_cores': psutil.cpu_count(logical=False),
        'total_cores': psutil.cpu_count(logical=True),
        'ram_total': round(psutil.virtual_memory().total / (1024.0 ** 3)),
        'ram_available': round(psutil.virtual_memory().available / (1024.0 ** 3)),
        'ram_used_percent': psutil.virtual_memory().percent
    }


def get_path_metadata():
    """
    Records the path information.

    Return a dictionary containing the path metadata.
    """
    # List all executable commands by scanning the PATH directories
    paths = os.environ['PATH'].split(os.pathsep)
    commands = set()
    for path in paths:
        if os.path.exists(path):
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path) and os.access(item_path, os.X_OK):
                        commands.add(item)
            except PermissionError:
                # This can happen if we don't have permission to list the contents of the directory
                continue

    return {
        "user": os.getlogin(),
        "current_directory": os.getcwd(),
        "home_directory": os.path.expanduser("~"),
        "executable_commands": sorted(list(commands))
    }


def get_file_metadata():
    """
    get_file_metadata: Records the file information in the current directory.
    """
    result = {
        "directory": [],
        "files": [],
        "invisible_files": [],
        "invisible_directory": []
    }

    # Get the current directory
    current_directory = os.getcwd()

    # List all files and directories in the current directory
    for item in os.listdir(current_directory):
        # Build the full path of the item
        item_path = os.path.join(current_directory, item)
        # Check if the item is invisible (hidden)
        if item.startswith('.'):
            if os.path.isdir(item_path):
                result["invisible_directory"].append(item)
            else:
                result["invisible_files"].append(item)
        else:
            if os.path.isdir(item_path):
                result["directory"].append(item)
            else:
                result["files"].append(item)

    return result


def get_python_metadata():
    """
    get_python_metadata: Records the Python-related environment.

    Return: a dictionary containing the Python-related metadata.
    """
    process = subprocess.run(["pip", "list"], capture_output=True, text=True)
    pip_list_lines = process.stdout.strip().split("\n")[2:]  # Skip the header lines
    pip_list = []
    for line in pip_list_lines:
        match = re.match(r"(\S+)\s+(\S+)(?:\s+(.*))?", line)
        if match:
            pip_list.append({
                "package": match.group(1),
                "version": match.group(2),
                "location": match.group(3)
            })

    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "python_compiler": platform.python_compiler(),
        "python_implementation": platform.python_implementation(),
        "python_build": platform.python_build(),
        "python_pip_packages": pip_list[2:],
    }


def get_gpu_metadata():
    """
    get_gpu_metadata: Records the GPU-related environment.

    Return: a dictionary containing the GPU-related metadata.
    """
    gpu_model_name = ""
    gpu_driver_version = ""
    cuda_version = ""
    if shutil.which("nvidia-smi"):
        p = subprocess.run([
            "nvidia-smi",
            "--query-gpu=gpu_name,driver_version",
            "--format=csv,noheader"
        ], capture_output=True)
        smi_string = p.stdout.decode("utf-8").strip().split("\n")
        if len(smi_string) == 1:
            gpu_model_name, gpu_driver_version = smi_string[0].split(",")
        else:
            gpu_model_name, gpu_driver_version = smi_string[0].split(",")
            for smi_entry in smi_string[1:]:
                other_model_name, other_driver_version = smi_entry.split(",")
                if other_model_name != gpu_model_name or other_driver_version != gpu_driver_version:
                    raise EnvironmentError("System is configured with different GPU models or driver versions.")

    if shutil.which("nvcc"):
        p = subprocess.run(["nvcc", "--version"], capture_output=True)
        match = re.search("\n.*release ([0-9]+\.[0-9]+).*\n", p.stdout.decode("utf-8"))
        cuda_version = match.group(1)

    return {
        "gpu_model_name": gpu_model_name,
        "gpu_driver_version": gpu_driver_version,
        "cuda_version": cuda_version,
    }


def get_command_history():
    """
    get_command_history: Get the command history of the current user including command times for zsh.

    :return: A list of dictionaries with 'command' and optionally 'time' keys, where 'time' is in datetime format.
    """
    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        # Attempt to detect the default shell from the $SHELL environment variable or /etc/passwd
        import pwd
        shell = os.environ.get('SHELL', pwd.getpwnam(getpass.getuser()).pw_shell)

        if 'bash' in shell:
            shell_type = 'bash'
            history_file = os.path.join(os.environ['HOME'], '.bash_history')
            history_format = 'plain'
        elif 'zsh' in shell:
            shell_type = 'zsh'
            history_file = os.path.join(os.environ['HOME'], '.zsh_history')
            history_format = 'with_time'
        elif 'fish' in shell: # [TODO] Add a support for fish shell
            shell_type = 'fish'
            history_file = os.path.join(os.environ['HOME'], '.local/share/fish/fish_history')
            history_format = 'yaml'
        else:
            raise ValueError(f"Shell not supported or history file unknown for shell: {shell}")

    elif sys.platform == 'win32':
        shell_type = 'powershell'
        history_file = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'PowerShell', 'PSReadLine',
                                    'ConsoleHost_history.txt')
        history_format = 'plain'
    else:
        raise ValueError(f"Platform not supported: {sys.platform}")

    try:
        history_lines = []
        with open(history_file, 'rb') as file:  # Open as binary to handle potential non-UTF characters
            for line in file:
                try:
                    # Decode each line individually, replace errors
                    decoded_line = line.decode('utf-8', 'replace').strip()
                    if history_format == 'with_time' and shell_type == 'zsh':
                        # Regex to parse zsh history with timestamps
                        match = re.match(r'^: (\d+):\d+;(.*)', decoded_line)
                        if match:
                            # Convert epoch time to datetime object and format it
                            epoch_time = int(match.group(1))
                            datetime_obj = datetime.fromtimestamp(epoch_time)
                            formatted_time = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
                            history_lines.append({
                                'command': match.group(2).strip(),
                                'time': formatted_time
                            })
                    elif history_format == 'yaml' and shell_type == 'fish':
                        if decoded_line.startswith('- cmd:'):
                            command_match = re.match(r'^- cmd: (.*)', decoded_line)
                            command = command_match.group(1).strip() if command_match else None
                        if decoded_line.startswith('when:'):
                            time_match = re.match(r'^when: (\d+)', decoded_line)
                            if time_match:
                                epoch_time = int(time_match.group(1))
                                datetime_obj = datetime.fromtimestamp(epoch_time)
                                formatted_time = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
                                history_lines.append({
                                    'command': command,
                                    'time': formatted_time
                                })
                    else:
                        history_lines.append({'command': decoded_line, 'time': None})
                except UnicodeDecodeError:
                    # In case decoding fails, skip the line or handle appropriately
                    continue
            # Return all commands
            return {"shell_command_history": history_lines[::-1]}
    except Exception as e:
        return f"Failed to read history file: {e}"
