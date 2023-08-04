from typing import Optional
import subprocess
from src.ai.print import ai_print, info_print
from src.ai.agi import run_agi

python_env = {}

SYSC_NONE = 0
SYSC_EXIT = 1
SYSC_SAY_NOTHING = 2

def python_excuter(code: str) -> (str, Optional[str]):
    result = exec(code, python_env)
    return result, SYSC_NONE


def shell_excuter(command: str) -> (str, Optional[str]):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if process.returncode != 0:
        return error.decode("utf-8"), SYSC_NONE
    else:
        return output.decode("utf-8"), SYSC_NONE


def exit_shell(props, see_you_text: str):
    ai_print(see_you_text)
    return "", SYSC_EXIT


def run_code(props, code: str, language: str):
    info_print(f"code: {code}")
    try:
        if language == "python":
            code_output = python_excuter(code)
        elif language == "shell":
            code_output = shell_excuter(code)
            code_output = f"""
result of {code} in {language}:
{code_output}
            """

        return code_output, SYSC_NONE
    except Exception as e:
        return f"error occured: {e}", SYSC_NONE


def just_acknowledgment(props):
    return "ai acknowledged.",SYSC_SAY_NOTHING


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
    },
    'just_acknowledgment': {
        'function': just_acknowledgment,
        'args': [
        ]
    },
    'run_agi': {
        'function': run_agi,
        'args': [
            "query",
            "epoch"
        ]
    },
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
        "description": "Helpful when user wants to run python || shell code and get output from repl. only excute if user says 'use interpreter'.",
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
    },
    {
        "name": "just_acknowledgment",
        "description": "Helpful when ai wants to just acknowledgment user. ex: user says 'well...' then ai calls this function to acknowledgment user.",
        "parameters": {
            "type": "object",
            "properties": {
            }
        },
        "required": []
    },
    {
        "name": "run_agi",
        "description": "Helpful when user wants to run agi and get output from agi. only excute if user says 'use agi'.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "query to run. e.g. why is autism so rare?"
                },
                "epoch": {
                    "type": "string",
                    "description": "epoch to run. e.g. 3. default is 3, max is 10."
                }
            }
        },
        "required": ["query", "epoch"]
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

        try:
            return function(props, **{arg: (function_args.get(arg)) for arg in args})
        except Exception as e:
            return f"error occured: {e}"
    else:
        return None
