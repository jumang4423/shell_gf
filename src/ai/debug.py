# debug console
impl_fn_arr = [
    "exit",
    "show_memory",
    "show_memory_agi",
]


def debug_shell():
    print("debug shell")
    print(f"implemented functions:")
    for i, v in enumerate(impl_fn_arr):
        print(f"{i}: {v}")

    while True:
        user_fn_number = input("debug> ")
        try:
            user_fn_number = int(user_fn_number)
            if user_fn_number >= len(impl_fn_arr):
                raise Exception("out of range")
            if user_fn_number < 0:
                raise Exception("out of range")
            if impl_fn_arr[user_fn_number] == "exit":
                break
            elif impl_fn_arr[user_fn_number] == "show_memory":
                print("NI")
            elif impl_fn_arr[user_fn_number] == "show_memory_agi":
                print("NI")
        except Exception as e:
            print(f"! Error: {e}")
            print()

    print("debug shell exited.")
