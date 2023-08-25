from src.ai.print import ai_print, user_print, error_print, warning_print, info_print


def welcome_text():
    info_print("shell_gf: shell chatbot for hackers")
    info_print("loading shell_gf...", end="", flush=True)


welcome_text()

import argparse
from src.ai.openai import step
from src.ai.debug import debug_shell
from src.ai.fc import fc_list
from src.ai.openai import GPT_4, JUMANGO

# get args
parser = argparse.ArgumentParser()
parser.add_argument("--speak", help="speak the output", action="store_true")
parser.add_argument("--jumango", help="use jumango", action="store_true")
args = parser.parse_args()
is_speak = args.speak
is_jumango = args.jumango
assert isinstance(is_speak, bool)
assert isinstance(is_jumango, bool)

print()
info_print(f"implemented functions list: {str(fc_list())}")
warning_print("type 'debug' to enter debug shell.")

while True:
    user_prompt = input("> ")
    try:
        if len(user_prompt) == 0:
            continue
        if user_prompt == "debug":
            debug_shell()
            continue
        user_print("* ", flush=True, end="")
        model = JUMANGO if is_jumango else GPT_4
        step(user_prompt, model, is_speak=is_speak, is_fc=not is_jumango)
    except Exception as e:
        error_print(f"! Error: {e}")
        print()
        exit(1)
