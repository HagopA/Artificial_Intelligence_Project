import os
import sys

# Disable printing
def toggle_printing_off():
    sys.stdout = open(os.devnull, 'w')

# Enable printing
def toggle_printing_on(stdout):
    sys.stdout = stdout

class TogglePrintingOffGuard:
    def __init__(self):
        self.previous_stdout_cache = sys.stdout
    def __enter__(self):
        toggle_printing_off()
    def __exit__(self, type, value, traceback):
        sys.stdout.close()
        toggle_printing_on(self.previous_stdout_cache)

# Add this decorator to a function to disable printing until exiting from it.
# This is very useful when AI is executing its moves, since it is not a human user and
# thus will not respond to warning or error messages we print to help the human user.
def toggle_printing_off_decorator(decorated_function):
    def decorate(*args, **kwargs):
        with TogglePrintingOffGuard():
            decorated_function(*args, **kwargs)
    return decorate