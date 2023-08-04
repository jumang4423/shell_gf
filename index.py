from src.ai.print import (
    ai_print,
    user_print,
    error_print,
    warning_print,
    info_print
)


def welcome_text():
    info_print("shell_gf: shell chatbot for hackers")
    info_print("loading shell_gf...", end="", flush=True)

welcome_text()

from src.ai.openai import step
from src.ai.debug import debug_shell
from src.ai.fc import fc_list
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
        step(user_prompt)
    except Exception as e:
        error_print(f"! Error: {e}")
        print()
        exit(1)
