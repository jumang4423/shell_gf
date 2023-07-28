from src.ai.print import (
    ai_print,
    user_print,
    error_print,
    info_print
)
from src.ai.fc import fc_list

def welcome_text():
    info_print("shell_gf: shell chatbot for hackers")
    info_print(f"implemented functions list: {str(fc_list())}")
    info_print("loading shell_gf...", end="", flush=True)

welcome_text()

from src.ai.openai import step
print()
while True:
    user_prompt = input("> ")
    try:
        if len(user_prompt) == 0:
            continue
        user_print("* ", flush=True, end="")
        step(user_prompt)
    except Exception as e:
        error_print(f"! Error: {e}")
        print()
        exit(1)
