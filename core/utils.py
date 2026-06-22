import sys
import os

def get_resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        # Запущено как PyInstaller EXE
        base_path = sys._MEIPASS
    else:
        # Запущено из Python
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)