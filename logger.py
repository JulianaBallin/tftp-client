"""
Módulo de logs coloridos para o cliente TFTP.

Fornece funções para exibir mensagens com cores no terminal,
facilitando a identificação de diferentes níveis (info, sucesso, aviso, erro).
"""

import sys
from enum import Enum

# Cores ANSI
class Color(Enum):
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

def _colorize(text: str, color: Color) -> str:
    return f"{color.value}{text}{Color.RESET.value}"

def info(msg: str):
    print(_colorize(msg, Color.CYAN))

def success(msg: str):
    print(_colorize(msg, Color.GREEN))

def warning(msg: str):
    print(_colorize(msg, Color.YELLOW))

def error(msg: str):
    print(_colorize(msg, Color.RED), file=sys.stderr)

def debug(msg: str):
    # Opcional: só exibir se DEBUG ativado
    print(_colorize(msg, Color.MAGENTA))
    