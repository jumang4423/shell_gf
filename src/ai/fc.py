from typing import Optional
from src.ai.print import ai_print

def python_excuter(code: str) -> str:
    result = exec(code)
    return result

def exit_shell(props, see_you_text: str):
    ai_print(see_you_text)
    exit(0)


def run_python_code(props, code: str):
    code_output = python_excuter(code)
    return code_output

function_mapping = {
    'exit': {
        'function': exit_shell,
        'args': [
            "see_you_text"
        ]
    },
    'run_python_code': {
        'function': run_python_code,
        'args': [
            "code"
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
        "name": "run_python_code",
        "description": "Helpful when user wants to run python code and get output from repl.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "python code to run. e.g. 3 + 3"
                }
            }
        },
        "required": ["code"]
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
