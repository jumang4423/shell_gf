from typing import Optional


def exit_shell(props):
    print("bye! nice hacking!")
    exit(0)

function_mapping = {
    'exit': {
        'function': exit_shell,
        'args': []
    },
}

function_struct = [
    {
        "name": "exit",
        "description": "helpful when user wants to exit our conversation.",
        "parameters": {
            "type": "object",
            "properties": {}
        },
        "required": []
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
