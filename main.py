"""
Ponto de entrada principal do cliente TFTP.

Decide entre modo interativo (menu) e modo linha de comando,
conforme a presença de argumentos na execução.
"""

import sys
from cli import menu_interativo, linha_comando

def main():
    if len(sys.argv) > 1:
        # Se houver argumentos, assume modo linha de comando
        linha_comando()
    else:
        # Caso contrário, entra no menu interativo
        menu_interativo()

if __name__ == "__main__":
    main()