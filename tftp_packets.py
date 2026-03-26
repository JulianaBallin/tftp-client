"""
Módulo para codificação e decodificação de pacotes TFTP conforme RFC 1350.

Este módulo fornece funções para criar e interpretar os cinco tipos de pacotes
do protocolo TFTP: RRQ, WRQ, DATA, ACK e ERROR.
"""

import struct
from enum import IntEnum


class Opcode(IntEnum):
    """Códigos de operação do TFTP (RFC 1350, seção 5)."""
    RRQ = 1
    WRQ = 2
    DATA = 3
    ACK = 4
    ERROR = 5


class ErrorCode(IntEnum):
    """Códigos de erro do TFTP (RFC 1350, seção 6)."""
    NOT_DEFINED = 0
    FILE_NOT_FOUND = 1
    ACCESS_VIOLATION = 2
    DISK_FULL = 3
    ILLEGAL_OPERATION = 4
    UNKNOWN_TID = 5
    FILE_EXISTS = 6
    NO_SUCH_USER = 7


def criar_rrq(nome_arquivo: str, modo: str = "octet") -> bytes:
    """
    Cria um pacote de solicitação de leitura (RRQ).

    Args:
        nome_arquivo: Nome do arquivo solicitado.
        modo: Modo de transferência ("octet" ou "netascii").

    Returns:
        Pacote RRQ em bytes pronto para envio.
    """
    # Opcode (2 bytes) + nome_arquivo + 0x00 + modo + 0x00
    opcode = struct.pack("!H", Opcode.RRQ)
    return opcode + nome_arquivo.encode() + b"\x00" + modo.encode() + b"\x00"


def criar_wrq(nome_arquivo: str, modo: str = "octet") -> bytes:
    """
    Cria um pacote de solicitação de escrita (WRQ).

    Args:
        nome_arquivo: Nome do arquivo a ser escrito.
        modo: Modo de transferência ("octet" ou "netascii").

    Returns:
        Pacote WRQ em bytes pronto para envio.
    """
    opcode = struct.pack("!H", Opcode.WRQ)
    return opcode + nome_arquivo.encode() + b"\x00" + modo.encode() + b"\x00"


def criar_data(bloco: int, dados: bytes) -> bytes:
    """
    Cria um pacote DATA.

    Args:
        bloco: Número do bloco (1 a 65535).
        dados: Conteúdo do bloco (até 512 bytes).

    Returns:
        Pacote DATA em bytes pronto para envio.
    """
    opcode = struct.pack("!H", Opcode.DATA)
    num_bloco = struct.pack("!H", bloco)
    return opcode + num_bloco + dados


def criar_ack(bloco: int) -> bytes:
    """
    Cria um pacote de confirmação (ACK).

    Args:
        bloco: Número do bloco sendo confirmado.

    Returns:
        Pacote ACK em bytes pronto para envio.
    """
    opcode = struct.pack("!H", Opcode.ACK)
    num_bloco = struct.pack("!H", bloco)
    return opcode + num_bloco


def criar_error(codigo: ErrorCode, mensagem: str = "") -> bytes:
    """
    Cria um pacote de erro.

    Args:
        codigo: Código de erro (ErrorCode).
        mensagem: Mensagem de erro opcional.

    Returns:
        Pacote ERROR em bytes pronto para envio.
    """
    opcode = struct.pack("!H", Opcode.ERROR)
    codigo_bytes = struct.pack("!H", codigo)
    return opcode + codigo_bytes + mensagem.encode() + b"\x00"


def decodificar_pacote(dados: bytes) -> dict:
    """
    Decodifica um pacote TFTP e retorna um dicionário com suas informações.

    Args:
        dados: Pacote bruto recebido.

    Returns:
        Dicionário com opcode e campos específicos do tipo de pacote.
        Exemplo: {"opcode": Opcode.DATA, "bloco": 1, "dados": b"..."}
        Em caso de erro ou formato inválido, retorna None.
    """
    if len(dados) < 4:
        return None

    opcode = struct.unpack("!H", dados[0:2])[0]

    if opcode == Opcode.DATA:
        if len(dados) < 4:
            return None
        bloco = struct.unpack("!H", dados[2:4])[0]
        return {
            "opcode": Opcode.DATA,
            "bloco": bloco,
            "dados": dados[4:]
        }

    elif opcode == Opcode.ACK:
        if len(dados) < 4:
            return None
        bloco = struct.unpack("!H", dados[2:4])[0]
        return {
            "opcode": Opcode.ACK,
            "bloco": bloco
        }

    elif opcode == Opcode.ERROR:
        if len(dados) < 5:
            return None
        codigo = struct.unpack("!H", dados[2:4])[0]
        mensagem = dados[4:].split(b"\x00")[0].decode("utf-8", errors="replace")
        return {
            "opcode": Opcode.ERROR,
            "codigo": codigo,
            "mensagem": mensagem
        }

    elif opcode in (Opcode.RRQ, Opcode.WRQ):
        # Para RRQ/WRQ, extraímos nome do arquivo e modo
        partes = dados[2:].split(b"\x00")
        if len(partes) < 2:
            return None
        nome_arquivo = partes[0].decode("utf-8", errors="replace")
        modo = partes[1].decode("utf-8", errors="replace") if len(partes) > 1 else "octet"
        return {
            "opcode": opcode,
            "nome_arquivo": nome_arquivo,
            "modo": modo
        }

    return None
