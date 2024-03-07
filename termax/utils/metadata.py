import re
import os
import sys
import psutil
import socket
import shutil
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
        "user_directory": os.path.expanduser("~"),
        "executable_commands": sorted(list(commands))
    }


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


if __name__ == "__main__":
    print(get_git_metadata())
    print(get_system_metadata())
    print(get_python_metadata())
    print(get_gpu_metadata())
    print(get_path_metadata())
