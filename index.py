from src.ai.openai import step
from src.ai.fc import fc_list


def welcome_text():
    print("shell_gf: shell chatbot for hackers")
    print(f"implemented functions list: {str(fc_list())}")

welcome_text()
while True:
    user_prompt = input("> ")
    try:
        if len(user_prompt) == 0:
            continue
        print("* ", end="")
        step(user_prompt)
    except Exception as e:
        print(f"! Error: {e}")
        exit(1)
