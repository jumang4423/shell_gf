from colored import Fore, Back, Style

def ai_print(text: str, flush: bool = False, end: str = "\n"):
    # green text with white background
    print(Fore.GREEN + text + Style.reset, end=end, flush=flush)

def user_print(text: str, flush: bool = False, end: str = "\n"):
    # white text with black background
    print(Fore.WHITE + text + Style.reset, end=end, flush=flush)

def error_print(text: str, end: str = "\n"):
    # red text with black background
    print(Fore.RED + text + Style.reset, end=end)
