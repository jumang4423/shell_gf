from typing import Optional
import subprocess
from src.ai.print import ai_print, info_print

python_env = {}

def python_excuter(code: str) -> str:
    result = exec(code, python_env)
    return result


def shell_excuter(command: str) -> str:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if process.returncode != 0:
        return error.decode("utf-8")
    else:
        return output.decode("utf-8")


def exit_shell(props, see_you_text: str):
    ai_print(see_you_text)
    exit(0)


def run_code(props, code: str, language: str):
    info_print(f"code: {code}")
    if language == "python":
        code_output = python_excuter(code)
    elif language == "shell":
        code_output = shell_excuter(code)
    code_output = f"""
result of {code} in {language}:
{code_output}
    """

    return code_output

function_mapping = {
    'exit': {
        'function': exit_shell,
        'args': [
            "see_you_text"
        ]
    },
    'run_code': {
        'function': run_code,
        'args': [
            "code",
            "language"
        ]
    }
}

function_struct = [
    {
        "name": "exit",
        "description": "helpful when user wants to exit our conversation.",
        "parameters": {
            "type": "object",
            "properties": {
                "see_you_text": {
                    "type": "string",
                    "description": "text to say when user wants to exit our conversation."
                }
            }
        },
        "required": ["see_you_text"]
    },
    {
        "name": "run_code",
        "description": "Helpful when user wants to run python || shell code and get output from repl.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "python code to run. e.g. 3 + 3"
                },
                "language": {
                    "type": "string",
                    "description": "language to run. e.g. python, shell",
                    "enum": ["python", "shell"]
                }
            }
        },
        "required": ["code", "language"]
    }
]

def fc_list() -> list[str]:
    return list(function_mapping.keys())


def resolver(props, function_name: str, function_args: dict) -> Optional[str]:
    if function_name in function_mapping:
        function = function_mapping[function_name]['function']
        args = function_mapping[function_name]['args']
        for arg in args:
            if arg not in function_args:
                function_args[arg] = ""

        return function(props, **{arg: (function_args.get(arg)) for arg in args})
    else:
        return None
