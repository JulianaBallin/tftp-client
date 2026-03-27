#!/usr/bin/env python3
"""
Cliente TFTP para linha de comando.

Implementa GET e PUT conforme RFC 1350, modo octet.
"""

import os
import socket
from tftp_packets import (
    Opcode,
    criar_ack,
    criar_data,
    criar_rrq,
    criar_wrq,
    decodificar_pacote,
)
from exceptions import (
    TFTPTimeoutError,
    TFTPProtocolError,
    TFTPFileError,
    TFTPTransferError,
)
import logger

class TFTPClient:
    def __init__(self, servidor: str, porta: int = 69, timeout: int = 5, max_retries: int = 5):
        self.servidor = servidor
        self.porta = porta
        self.timeout = timeout
        self.max_retries = max_retries
        self.socket = None
        self.porta_servidor_transferencia = porta

    def _enviar_com_retransmissao(self, dados: bytes, esperar_resposta: bool = True):
        """Envia dados e aguarda resposta com retransmissão."""
        for tentativa in range(self.max_retries):
            try:
                self.socket.sendto(dados, (self.servidor, self.porta_servidor_transferencia))
                if not esperar_resposta:
                    return (b"", None)

                self.socket.settimeout(self.timeout)
                resposta, endereco = self.socket.recvfrom(65535)

                if self.porta_servidor_transferencia == 69:
                    self.porta_servidor_transferencia = endereco[1]

                return (resposta, endereco)

            except socket.timeout:
                logger.warning(f"Timeout (tentativa {tentativa + 1}/{self.max_retries})")
                continue
            except socket.error as e:
                raise TFTPTransferError(f"Erro de socket: {e}")

        raise TFTPTimeoutError("Sem resposta do servidor após retentativas")

    def _tratar_erro_servidor(self, pacote: dict):
        """Levanta exceção com base no código de erro do servidor."""
        if pacote and pacote.get("opcode") == Opcode.ERROR:
            codigo = pacote.get("codigo")
            msg = pacote.get("mensagem", "")
            raise TFTPFileError(f"Servidor retornou erro {codigo}: {msg}")

    def _receber_bloco(self, bloco_esperado: int):
        """Aguarda e valida um bloco DATA, com retransmissão."""
        for tentativa in range(self.max_retries):
            try:
                self.socket.settimeout(self.timeout)
                resposta, _ = self.socket.recvfrom(65535)
                pacote = decodificar_pacote(resposta)

                if not pacote:
                    logger.warning("Pacote inválido, ignorando")
                    continue

                if pacote.get("opcode") == Opcode.ERROR:
                    self._tratar_erro_servidor(pacote)

                if pacote.get("opcode") != Opcode.DATA:
                    logger.warning(f"Pacote inesperado: opcode {pacote.get('opcode')}")
                    continue

                if pacote.get("bloco") != bloco_esperado:
                    logger.warning(f"Bloco esperado {bloco_esperado}, recebido {pacote.get('bloco')}")
                    # Reenvia ACK do último bloco correto
                    if bloco_esperado > 1:
                        ack = criar_ack(bloco_esperado - 1)
                        self.socket.sendto(ack, (self.servidor, self.porta_servidor_transferencia))
                    continue

                return pacote

            except socket.timeout:
                logger.warning(f"Timeout aguardando bloco {bloco_esperado} (tentativa {tentativa + 1})")
                if bloco_esperado > 1:
                    ack = criar_ack(bloco_esperado - 1)
                    self.socket.sendto(ack, (self.servidor, self.porta_servidor_transferencia))
                continue
            except socket.error as e:
                raise TFTPTransferError(f"Erro de socket: {e}")

        raise TFTPTimeoutError(f"Timeout após {self.max_retries} tentativas para bloco {bloco_esperado}")

    def get(self, nome_remoto: str, nome_local: str) -> bool:
        logger.info(f"Iniciando download: {nome_remoto} -> {nome_local}")

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.timeout)

            rrq = criar_rrq(nome_remoto, "octet")
            resposta, _ = self._enviar_com_retransmissao(rrq)

            pacote = decodificar_pacote(resposta)
            if not pacote or pacote.get("opcode") != Opcode.DATA:
                self._tratar_erro_servidor(pacote)
                raise TFTPProtocolError("Primeira resposta não é DATA")

            bloco_esperado = 1
            arquivo_bytes = bytearray()

            while True:
                if pacote.get("bloco") != bloco_esperado:
                    raise TFTPProtocolError(f"Esperado bloco {bloco_esperado}, recebido {pacote.get('bloco')}")

                dados = pacote.get("dados", b"")
                arquivo_bytes.extend(dados)

                ack = criar_ack(bloco_esperado)
                self.socket.sendto(ack, (self.servidor, self.porta_servidor_transferencia))

                if len(dados) < 512:  # último bloco
                    break

                bloco_esperado += 1
                pacote = self._receber_bloco(bloco_esperado)

            with open(nome_local, "wb") as f:
                f.write(arquivo_bytes)

            logger.success(f"Download concluído: {nome_local}")
            return True

        except Exception as e:
            logger.error(f"Erro no download: {e}")
            return False
        finally:
            if self.socket:
                self.socket.close()

    def put(self, nome_local: str, nome_remoto: str) -> bool:
        logger.info(f"Iniciando upload: {nome_local} -> {nome_remoto}")

        try:
            with open(nome_local, "rb") as f:
                dados_arquivo = f.read()
        except FileNotFoundError:
            logger.error(f"Arquivo local não encontrado: {nome_local}")
            return False
        except IOError as e:
            logger.error(f"Erro ao ler arquivo: {e}")
            return False

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.timeout)

            wrq = criar_wrq(nome_remoto, "octet")
            resposta, _ = self._enviar_com_retransmissao(wrq)

            pacote = decodificar_pacote(resposta)
            if not pacote or pacote.get("opcode") != Opcode.ACK or pacote.get("bloco") != 0:
                self._tratar_erro_servidor(pacote)
                raise TFTPProtocolError("Resposta esperada ACK(0) não recebida")

            bloco_atual = 1
            posicao = 0
            tamanho_bloco = 512

            while posicao < len(dados_arquivo):
                bloco_dados = dados_arquivo[posicao:posicao + tamanho_bloco]
                pacote_dados = criar_data(bloco_atual, bloco_dados)

                # Envia com retransmissão
                resposta, _ = self._enviar_com_retransmissao(pacote_dados)
                pacote = decodificar_pacote(resposta)
                if not pacote or pacote.get("opcode") != Opcode.ACK:
                    self._tratar_erro_servidor(pacote)
                    raise TFTPProtocolError(f"ACK não recebido para bloco {bloco_atual}")

                if pacote.get("bloco") != bloco_atual:
                    raise TFTPProtocolError(f"ACK inesperado: esperado {bloco_atual}, recebido {pacote.get('bloco')}")

                bloco_atual += 1
                posicao += tamanho_bloco

                if bloco_atual % 50 == 0:
                    prog = min(100, int(posicao * 100 / len(dados_arquivo)))
                    logger.info(f"Progresso: {prog}%")

            # Bloco final vazio (opcional)
            try:
                pacote_final = criar_data(bloco_atual, b"")
                self.socket.sendto(pacote_final, (self.servidor, self.porta_servidor_transferencia))
            except:
                pass

            logger.success(f"Upload concluído: {len(dados_arquivo)} bytes")
            return True

        except Exception as e:
            logger.error(f"Erro no upload: {e}")
            return False
        finally:
            if self.socket:
                self.socket.close()
                
    def criar_pasta_servidor(self, caminho_completo: str) -> bool:
        """
        Tenta criar a estrutura de pastas no servidor enviando um arquivo vazio.
        Retorna True se a pasta existe ou foi criada com sucesso.
        """
        # Verifica se o caminho tem pasta (ex: "grupo4/arquivo.txt")
        partes = caminho_completo.split('/')
        if len(partes) <= 1:
            return True  # sem pasta, já existe
        
        nome_pasta = partes[0]
        arquivo_teste = f"{nome_pasta}/.tftp_test_{os.getpid()}"
        
        try:
            # Cria um socket temporário
            socket_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_temp.settimeout(self.timeout)
            
            # Envia WRQ para o arquivo de teste
            wrq = criar_wrq(arquivo_teste, "octet")
            socket_temp.sendto(wrq, (self.servidor, self.porta))
            
            # Aguarda resposta
            socket_temp.settimeout(self.timeout)
            resposta, endereco = socket_temp.recvfrom(65535)
            
            pacote = decodificar_pacote(resposta)
            
            # Se recebeu ACK(0), a pasta existe ou foi criada
            if pacote and pacote.get("opcode") == Opcode.ACK and pacote.get("bloco") == 0:
                # Envia um bloco vazio para finalizar a transferência
                dados_vazios = criar_data(1, b"")
                socket_temp.sendto(dados_vazios, (self.servidor, endereco[1]))
                logger.debug(f"Pasta '{nome_pasta}' criada ou já existe")
                socket_temp.close()
                return True
            
            # Se recebeu erro, pode ser que a pasta não exista
            if pacote and pacote.get("opcode") == Opcode.ERROR:
                logger.debug(f"Erro ao criar pasta: {pacote.get('mensagem')}")
                socket_temp.close()
                return False
                
            socket_temp.close()
            return False
            
        except socket.timeout:
            logger.debug("Timeout ao tentar criar pasta")
            return False
        except Exception as e:
            logger.debug(f"Erro ao criar pasta: {e}")
            return False