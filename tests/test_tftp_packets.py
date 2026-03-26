import unittest
import struct
from tftp_packets import (
    Opcode,
    ErrorCode,
    criar_rrq,
    criar_wrq,
    criar_data,
    criar_ack,
    criar_error,
    decodificar_pacote,
)


class TestPacketEncoding(unittest.TestCase):
    def test_rrq(self):
        pacote = criar_rrq("teste.txt", "octet")
        # Opcode (1) + "teste.txt" + 0 + "octet" + 0
        esperado = struct.pack("!H", 1) + b"teste.txt\x00octet\x00"
        self.assertEqual(pacote, esperado)

    def test_wrq(self):
        pacote = criar_wrq("outro.txt", "netascii")
        esperado = struct.pack("!H", 2) + b"outro.txt\x00netascii\x00"
        self.assertEqual(pacote, esperado)

    def test_data(self):
        dados = b"conteudo"
        pacote = criar_data(42, dados)
        # Opcode (3) + bloco (42) + dados
        esperado = struct.pack("!H", 3) + struct.pack("!H", 42) + dados
        self.assertEqual(pacote, esperado)

    def test_ack(self):
        pacote = criar_ack(99)
        esperado = struct.pack("!H", 4) + struct.pack("!H", 99)
        self.assertEqual(pacote, esperado)

    def test_error(self):
        pacote = criar_error(ErrorCode.FILE_NOT_FOUND, "Arquivo nao encontrado")
        esperado = struct.pack("!H", 5) + struct.pack("!H", 1) + b"Arquivo nao encontrado\x00"
        self.assertEqual(pacote, esperado)


class TestPacketDecoding(unittest.TestCase):
    def test_decode_rrq(self):
        raw = struct.pack("!H", 1) + b"teste.txt\x00octet\x00"
        dec = decodificar_pacote(raw)
        self.assertEqual(dec["opcode"], Opcode.RRQ)
        self.assertEqual(dec["nome_arquivo"], "teste.txt")
        self.assertEqual(dec["modo"], "octet")

    def test_decode_wrq(self):
        raw = struct.pack("!H", 2) + b"outro.txt\x00netascii\x00"
        dec = decodificar_pacote(raw)
        self.assertEqual(dec["opcode"], Opcode.WRQ)
        self.assertEqual(dec["nome_arquivo"], "outro.txt")
        self.assertEqual(dec["modo"], "netascii")

    def test_decode_data(self):
        raw = struct.pack("!H", 3) + struct.pack("!H", 7) + b"abcde"
        dec = decodificar_pacote(raw)
        self.assertEqual(dec["opcode"], Opcode.DATA)
        self.assertEqual(dec["bloco"], 7)
        self.assertEqual(dec["dados"], b"abcde")

    def test_decode_ack(self):
        raw = struct.pack("!H", 4) + struct.pack("!H", 12)
        dec = decodificar_pacote(raw)
        self.assertEqual(dec["opcode"], Opcode.ACK)
        self.assertEqual(dec["bloco"], 12)

    def test_decode_error(self):
        raw = struct.pack("!H", 5) + struct.pack("!H", 1) + b"Erro\x00"
        dec = decodificar_pacote(raw)
        self.assertEqual(dec["opcode"], Opcode.ERROR)
        self.assertEqual(dec["codigo"], 1)
        self.assertEqual(dec["mensagem"], "Erro")

    def test_decode_invalid(self):
        self.assertIsNone(decodificar_pacote(b"abc"))


if __name__ == "__main__":
    unittest.main()