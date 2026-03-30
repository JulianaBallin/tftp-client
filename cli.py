"""
Interface de linha de comando e menu interativo.

Implementa duas formas de uso: via argparse (comandos diretos) e
via menu interativo (para testes manuais). Encapsula a interação
com o usuário e chama o cliente TFTP correspondente.
"""

import os
import sys
from pathlib import Path

from client import TFTPClient
import logger

# Diretórios locais
PASTA_DOWNLOADS = Path("downloads")
PASTA_UPLOADS = Path("uploads")


def garantir_pastas():
    """Cria as pastas locais se não existirem."""
    PASTA_DOWNLOADS.mkdir(exist_ok=True)
    PASTA_UPLOADS.mkdir(exist_ok=True)


def listar_arquivos_local(pasta: Path) -> list[str]:
    """Retorna lista de nomes de arquivos em uma pasta."""
    if not pasta.exists():
        return []
    return [f.name for f in pasta.iterdir() if f.is_file()]


def montar_caminho_remoto(nome_arquivo: str) -> str:
    """
    Monta o caminho remoto opcionalmente com uma pasta no servidor.

    Args:
        nome_arquivo: Nome base do arquivo remoto.

    Returns:
        Caminho remoto final informado pelo usuário.
    """
    usar_pasta = input(
        "Deseja usar uma pasta no servidor? (ex: grupo4) [s/N]: "
    ).strip().lower()

    if usar_pasta == "s":
        pasta = input("Nome da pasta no servidor: ").strip().strip("/")
        if pasta:
            return f"{pasta}/{nome_arquivo}"

    return nome_arquivo


def menu_interativo():
    """Menu principal com opções de GET, PUT e sair."""
    garantir_pastas()

    while True:
        print("\n" + "=" * 50)
        logger.info("=== Cliente TFTP - GRUPO 4 ===")
        print("=" * 50)
        print("1. Baixar arquivo (GET) -> salva em 'downloads/'")
        print("2. Enviar arquivo   (PUT)  -> lê de 'uploads/'")
        print("3. Listar arquivos baixados")
        print("4. Listar arquivos para upload")
        print("5. Sair")
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            host = input("Host do servidor: ").strip()
            if not host:
                host = "127.0.0.1"

            porta = input("Porta (padrão 69): ").strip()
            porta = int(porta) if porta else 69

            remoto = input("Nome do arquivo remoto: ").strip()
            if not remoto:
                logger.error("Nome do arquivo remoto é obrigatório.")
                continue

            remoto_completo = montar_caminho_remoto(remoto)
            logger.info(f"Buscando: {remoto_completo}")

            nome_local = Path(remoto).name
            local = PASTA_DOWNLOADS / nome_local

            cliente = TFTPClient(host, porta)
            cliente.get(remoto_completo, str(local))

        elif opcao == "2":
            host = input("Host do servidor: ").strip()
            if not host:
                host = "127.0.0.1"

            porta = input("Porta (padrão 69): ").strip()
            porta = int(porta) if porta else 69

            remoto = input("Nome do arquivo no servidor: ").strip()
            if not remoto:
                logger.error("Nome do arquivo remoto é obrigatório.")
                continue

            remoto_completo = montar_caminho_remoto(remoto)
            logger.info(f"Salvando em: {remoto_completo}")

            arquivos = listar_arquivos_local(PASTA_UPLOADS)
            if not arquivos:
                logger.warning(f"Nenhum arquivo em '{PASTA_UPLOADS}/'.")
                logger.info("Coloque os arquivos na pasta 'uploads/' e tente novamente.")
                input("Pressione Enter para voltar...")
                continue

            logger.info("Arquivos disponíveis:")
            for i, nome in enumerate(arquivos, 1):
                print(f"  {i}. {nome}")
            print("  0. Cancelar")

            escolha = input("Escolha o número: ").strip()
            if escolha == "0":
                continue

            try:
                idx = int(escolha) - 1
                if 0 <= idx < len(arquivos):
                    local_path = PASTA_UPLOADS / arquivos[idx]

                    tamanho_bytes = os.path.getsize(local_path)
                    tamanho_mb = tamanho_bytes / (1024 * 1024)

                    if tamanho_bytes > (65535 * 512):
                        logger.warning(
                            f"Arquivo tem {tamanho_mb:.2f} MB, pode exceder limite do servidor."
                        )
                        confirmar = input("Continuar? (s/N): ").strip().lower()
                        if confirmar != "s":
                            continue

                    extensao = os.path.splitext(local_path)[1]
                    if not remoto_completo.endswith(extensao) and extensao:
                        sugestao = remoto_completo + extensao
                        logger.info(f"Sugestão: {sugestao}")
                        usar = input("Usar este nome? (s/N): ").strip().lower()
                        if usar == "s":
                            remoto_completo = sugestao

                    cliente = TFTPClient(host, porta)
                    resultado = cliente.put(str(local_path), remoto_completo)

                    if not resultado:
                        logger.warning("Falha no upload.")
                        logger.info(
                            "Verifique se o caminho remoto existe e se o servidor permite "
                            "escrita/criação de arquivos."
                        )
                        logger.info(
                            "Se o servidor não usar subpastas, informe apenas o nome do arquivo."
                        )
                else:
                    logger.error("Número inválido.")

            except ValueError:
                logger.error("Entrada inválida.")
            except OSError as error:
                logger.error(f"Erro ao ler arquivo: {error}")

        elif opcao == "3":
            arquivos = listar_arquivos_local(PASTA_DOWNLOADS)
            if not arquivos:
                logger.info("Nenhum arquivo baixado ainda.")
            else:
                logger.info("Arquivos baixados:")
                for nome in arquivos:
                    print(f"  - {nome}")
            input("Pressione Enter para continuar...")

        elif opcao == "4":
            arquivos = listar_arquivos_local(PASTA_UPLOADS)
            if not arquivos:
                logger.info("Nenhum arquivo disponível para upload.")
                logger.info("Coloque os arquivos na pasta 'uploads/' e tente novamente.")
            else:
                logger.info("Arquivos para upload:")
                for nome in arquivos:
                    print(f"  - {nome}")
            input("Pressione Enter para continuar...")

        elif opcao == "5":
            logger.info("Encerrando...")
            break

        else:
            logger.error("Opção inválida.")


def linha_comando():
    """Interface via linha de comando (argparse)."""
    import argparse

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
    