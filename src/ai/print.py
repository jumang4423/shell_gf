from colored import Fore, Back, Style

def ai_print(text: str, flush: bool = False, end: str = "\n"):
    # green text with white background
    print(Fore.light_green + text + Style.reset, end=end, flush=flush)

def user_print(text: str, flush: bool = False, end: str = "\n"):
    # white text with black background
    print(Fore.white + text + Style.reset, end=end, flush=flush)

def info_print(text: str, end: str = "\n", flush: bool = False):
    print(Fore.light_blue + text + Style.reset, end=end, flush=flush)


def comment_print(text: str, end: str = "\n", flush: bool = False):
    # gray text with black background
    print(Fore.dark_gray + text + Style.reset, end=end, flush=flush)

def error_print(text: str, end: str = "\n"):
    # red text with black background
    print(Fore.RED + text + Style.reset, end=end)
