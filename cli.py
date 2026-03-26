"""
Interface de linha de comando e menu interativo.

Implementa duas formas de uso: via argparse (comandos diretos) e
via menu interativo (para testes manuais). Encapsula a interação
com o usuário e chama o cliente TFTP correspondente.
"""

import sys
import argparse
from client import TFTPClient
import logger

def menu_interativo():
    """Exibe um menu interativo para o usuário."""
    while True:
        print("\n" + "="*40)
        logger.info("1. Download (GET)")
        logger.info("2. Upload (PUT)")
        logger.info("3. Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            host = input("Host do servidor: ")
            porta = int(input("Porta (padrão 69): ") or "69")
            remoto = input("Arquivo remoto: ")
            local = input("Arquivo local: ")
            cliente = TFTPClient(host, porta)
            cliente.get(remoto, local)

        elif opcao == "2":
            host = input("Host do servidor: ")
            porta = int(input("Porta (padrão 69): ") or "69")
            local = input("Arquivo local: ")
            remoto = input("Arquivo remoto: ")
            cliente = TFTPClient(host, porta)
            cliente.put(local, remoto)

        elif opcao == "3":
            logger.info("Encerrando...")
            sys.exit(0)
        else:
            logger.error("Opção inválida")

def linha_comando():
    """Interface via linha de comando (argparse)."""
    parser = argparse.ArgumentParser(description="Cliente TFTP (RFC 1350)")
    subparsers = parser.add_subparsers(dest="comando")

    get_parser = subparsers.add_parser("get", help="Baixar arquivo")
    get_parser.add_argument("--host", required=True)
    get_parser.add_argument("--port", type=int, default=69)
    get_parser.add_argument("--remote", required=True)
    get_parser.add_argument("--local", required=True)
    get_parser.add_argument("--timeout", type=int, default=5)
    get_parser.add_argument("--retries", type=int, default=5)

    put_parser = subparsers.add_parser("put", help="Enviar arquivo")
    put_parser.add_argument("--host", required=True)
    put_parser.add_argument("--port", type=int, default=69)
    put_parser.add_argument("--local", required=True)
    put_parser.add_argument("--remote", required=True)
    put_parser.add_argument("--timeout", type=int, default=5)
    put_parser.add_argument("--retries", type=int, default=5)

    args = parser.parse_args()
    if not args.comando:
        parser.print_help()
        sys.exit(1)

    cliente = TFTPClient(
        servidor=args.host,
        porta=args.port,
        timeout=args.timeout,
        max_retries=args.retries,
    )

    ok = False
    if args.comando == "get":
        ok = cliente.get(args.remote, args.local)
    elif args.comando == "put":
        ok = cliente.put(args.local, args.remote)

    sys.exit(0 if ok else 1)
    