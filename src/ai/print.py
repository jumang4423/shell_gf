from colored import Fore, Back, Style

def ai_print(text: str, flush: bool = False, end: str = "\n"):
    # green text with white background
    print(Fore.light_green + text + Style.reset, end=end, flush=flush)

def user_print(text: str, flush: bool = False, end: str = "\n"):
    # white text with black background
    print(Fore.white + text + Style.reset, end=end, flush=flush)

def info_print(text: str, end: str = "\n"):
    print(Fore.light_blue + text + Style.reset, end=end)

def error_print(text: str, end: str = "\n"):
    # red text with black background
    print(Fore.RED + text + Style.reset, end=end)
