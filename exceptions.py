"""
Exceções personalizadas para o cliente TFTP.

Define hierarquia de erros específicos do protocolo e da rede,
permitindo tratamento granular durante as transferências.
"""

class TFTPError(Exception):
    """Exceção base para erros do TFTP."""
    pass

class TFTPTimeoutError(TFTPError):
    """Timeout na comunicação."""
    pass

class TFTPProtocolError(TFTPError):
    """Pacote inválido, opcode errado, etc."""
    pass

class TFTPFileError(TFTPError):
    """Arquivo não encontrado, permissão, etc."""
    pass

class TFTPTransferError(TFTPError):
    """Erro durante transferência (bloco perdido, etc)."""
    pass