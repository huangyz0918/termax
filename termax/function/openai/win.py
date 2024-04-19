from pydantic import Field
from instructor import OpenAISchema

from termax.prompt import process_powershell_script

class WinFunction(OpenAISchema):
    """
    Executes PowerShell script on Windows and returns the output (result).
    Can be used for actions like: starting applications, managing system tasks, or querying system information.
    """

    script: str = Field(
        ...,
        example='Write-Host "Hello World"',
        description="PowerShell script to execute."
    )

    class Config:
        title = "execute_powershell_script"

    @classmethod
    def execute(cls, script):
        processed_script = process_powershell_script(script)
        return f"powershell -Command {processed_script}"