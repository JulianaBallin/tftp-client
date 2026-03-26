"""
Codificação e decodificação de pacotes TFTP conforme RFC 1350.
"""

import struct
from enum import IntEnum


class Opcode(IntEnum):
    RRQ = 1
    WRQ = 2
    DATA = 3
    ACK = 4
    ERROR = 5


class ErrorCode(IntEnum):
    NOT_DEFINED = 0
    FILE_NOT_FOUND = 1
    ACCESS_VIOLATION = 2
    DISK_FULL = 3
    ILLEGAL_OPERATION = 4
    UNKNOWN_TID = 5
    FILE_EXISTS = 6
    NO_SUCH_USER = 7


def criar_rrq(nome_arquivo: str, modo: str = "octet") -> bytes:
    """Pacote de leitura (RRQ)."""
    opcode = struct.pack("!H", Opcode.RRQ)
    return opcode + nome_arquivo.encode() + b"\x00" + modo.encode() + b"\x00"


def criar_wrq(nome_arquivo: str, modo: str = "octet") -> bytes:
    """Pacote de escrita (WRQ)."""
    opcode = struct.pack("!H", Opcode.WRQ)
    return opcode + nome_arquivo.encode() + b"\x00" + modo.encode() + b"\x00"


def criar_data(bloco: int, dados: bytes) -> bytes:
    """Pacote de dados (DATA)."""
    opcode = struct.pack("!H", Opcode.DATA)
    num_bloco = struct.pack("!H", bloco)
    return opcode + num_bloco + dados


def criar_ack(bloco: int) -> bytes:
    """Pacote de confirmação (ACK)."""
    opcode = struct.pack("!H", Opcode.ACK)
    num_bloco = struct.pack("!H", bloco)
    return opcode + num_bloco


def criar_error(codigo: ErrorCode, mensagem: str = "") -> bytes:
    """Pacote de erro (ERROR)."""
    opcode = struct.pack("!H", Opcode.ERROR)
    codigo_bytes = struct.pack("!H", codigo)
    return opcode + codigo_bytes + mensagem.encode() + b"\x00"


def decodificar_pacote(dados: bytes) -> dict | None:
    """
    Converte bytes em dicionário com os campos do pacote.
    Retorna None se o pacote for inválido.
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
            "dados": dados[4:],
        }

    if opcode == Opcode.ACK:
        if len(dados) < 4:
            return None
        bloco = struct.unpack("!H", dados[2:4])[0]
        return {"opcode": Opcode.ACK, "bloco": bloco}

    if opcode == Opcode.ERROR:
        if len(dados) < 5:
            return None
        codigo = struct.unpack("!H", dados[2:4])[0]
        mensagem = dados[4:].split(b"\x00")[0].decode("utf-8", errors="replace")
        return {"opcode": Opcode.ERROR, "codigo": codigo, "mensagem": mensagem}

    if opcode in (Opcode.RRQ, Opcode.WRQ):
        partes = dados[2:].split(b"\x00")
        if len(partes) < 2:
            return None
        nome = partes[0].decode("utf-8", errors="replace")
        modo = partes[1].decode("utf-8", errors="replace") if len(partes) > 1 else "octet"
        return {"opcode": opcode, "nome_arquivo": nome, "modo": modo}

    return None