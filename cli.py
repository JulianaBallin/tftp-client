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
PASTA_SERVIDOR = "grupo4"  # pasta padrão no servidor

def garantir_pastas():
    """Cria as pastas locais se não existirem."""
    PASTA_DOWNLOADS.mkdir(exist_ok=True)
    PASTA_UPLOADS.mkdir(exist_ok=True)

def listar_arquivos_local(pasta: Path) -> list:
    """Retorna lista de nomes de arquivos em uma pasta."""
    if not pasta.exists():
        return []
    return [f.name for f in pasta.iterdir() if f.is_file()]

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
            # GET
            host = input("Host do servidor: ").strip()
            if not host:
                host = "127.0.0.1"
            porta = input("Porta (padrão 69): ").strip()
            porta = int(porta) if porta else 69
            remoto = input("Nome do arquivo remoto: ").strip()
            if not remoto:
                logger.error("Nome do arquivo remoto é obrigatório.")
                continue

            # Adiciona a pasta grupo4 no caminho
            remoto_completo = f"{PASTA_SERVIDOR}/{remoto}"
            logger.info(f"Buscando: {remoto_completo}")

            local = PASTA_DOWNLOADS / remoto
            cliente = TFTPClient(host, porta)
            cliente.get(remoto_completo, str(local))

        elif opcao == "2":
            # PUT com seleção de arquivo da pasta uploads
            host = input("Host do servidor: ").strip()
            if not host:
                host = "127.0.0.1"
            porta = input("Porta (padrão 69): ").strip()
            porta = int(porta) if porta else 69
            remoto = input("Nome do arquivo no servidor: ").strip()
            if not remoto:
                logger.error("Nome do arquivo remoto é obrigatório.")
                continue

            # Adiciona a pasta grupo4 no caminho
            remoto_completo = f"{PASTA_SERVIDOR}/{remoto}"
            logger.info(f"Salvando em: {remoto_completo}")

            # Lista arquivos disponíveis para upload
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

                    # Verifica tamanho do arquivo
                    tamanho_bytes = os.path.getsize(local_path)
                    tamanho_mb = tamanho_bytes / (1024 * 1024)

                    if tamanho_bytes > (65535 * 512):  # ~32 MB
                        logger.warning(f"Arquivo tem {tamanho_mb:.2f} MB, pode exceder limite do servidor.")
                        confirmar = input("Continuar? (s/N): ").strip().lower()
                        if confirmar != 's':
                            continue

                    # Sugere extensão automaticamente
                    extensao = os.path.splitext(local_path)[1]
                    if not remoto.endswith(extensao) and extensao:
                        sugestao = remoto + extensao
                        logger.info(f"Sugestão: {PASTA_SERVIDOR}/{sugestao}")
                        usar = input("Usar este nome? (s/N): ").strip().lower()
                        if usar == 's':
                            remoto_completo = f"{PASTA_SERVIDOR}/{sugestao}"

                    # --- TENTA O UPLOAD ---
                    cliente = TFTPClient(host, porta)
                    resultado = cliente.put(str(local_path), remoto_completo)
                    
                    # Se falhou, tenta criar a pasta
                    if not resultado:
                        logger.warning("Falha no upload. Pode ser que a pasta 'grupo4' não exista no servidor.")
                        criar = input("Tentar criar a pasta automaticamente? (s/N): ").strip().lower()
                        
                        if criar == 's':
                            logger.info("Tentando criar pasta 'grupo4' no servidor...")
                            cliente_temp = TFTPClient(host, porta, timeout=5, max_retries=2)
                            
                            if cliente_temp.criar_pasta_servidor(remoto_completo):
                                logger.success("Pasta criada ou já existente. Tentando upload novamente...")
                                resultado = cliente.put(str(local_path), remoto_completo)
                                if resultado:
                                    logger.success("Upload concluído após criar pasta!")
                                else:
                                    logger.error("Upload ainda falhou. Verifique as permissões do servidor.")
                            else:
                                logger.error("Não foi possível criar a pasta automaticamente.")
                                print("\n" + "=" * 60)
                                logger.info("📌 Para o administrador do servidor TFTP:")
                                print("")
                                print("   Execute os seguintes comandos no servidor:")
                                print("")
                                print("   sudo mkdir -p /srv/tftp/grupo4")
                                print("   sudo chmod 777 /srv/tftp/grupo4")
                                print("")
                                print("   Se o servidor estiver em outra porta ou diretório, ajuste o caminho.")
                                print("")
                                logger.info("Após criar a pasta, tente o upload novamente.")
                                print("=" * 60)
                        else:
                            logger.info("Upload cancelado.")
                    
                else:
                    logger.error("Número inválido.")
            except ValueError:
                logger.error("Entrada inválida.")
            except OSError as e:
                logger.error(f"Erro ao ler arquivo: {e}")

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
    """Interface via linha de comando (argparse) – mantida para compatibilidade."""
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

    # Adiciona pasta grupo4 para compatibilidade com linha de comando
    remote_completo = f"{PASTA_SERVIDOR}/{args.remote}" if args.comando in ["get", "put"] else args.remote

    cliente = TFTPClient(
        servidor=args.host,
        porta=args.port,
        timeout=args.timeout,
        max_retries=args.retries,
    )

    ok = False
    if args.comando == "get":
        ok = cliente.get(remote_completo, args.local)
    elif args.comando == "put":
        ok = cliente.put(args.local, remote_completo)

    sys.exit(0 if ok else 1)