from src.ai.openai import step
from src.ai.fc import fc_list
from src.ai.print import (
    ai_print,
    user_print,
    error_print
)

def welcome_text():
    ai_print("shell_gf: shell chatbot for hackers")
    ai_print(f"implemented functions list: {str(fc_list())}")

welcome_text()
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
