import unittest
from unittest.mock import patch, MagicMock
import socket
from client import TFTPClient

class TestTFTPClient(unittest.TestCase):
    def setUp(self):
        self.cliente = TFTPClient("127.0.0.1", 69, timeout=1, max_retries=1)

    @patch("socket.socket")
    def test_get_success(self, mock_socket):
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        # Simula DATA bloco 1 (512) e DATA bloco 2 (100)
        dados_bloco1 = b"X" * 512
        dados_bloco2 = b"Y" * 100
        pacote_data1 = b"\x00\x03\x00\x01" + dados_bloco1
        pacote_data2 = b"\x00\x03\x00\x02" + dados_bloco2

        mock_sock.recvfrom.side_effect = [
            (pacote_data1, ("127.0.0.1", 12345)),
            (pacote_data2, ("127.0.0.1", 12345))
        ]

        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            resultado = self.cliente.get("remoto.txt", "local.txt")
            self.assertTrue(resultado)
            # Verifica escrita
            escrito = mock_file().write.call_args[0][0]
            self.assertEqual(escrito, dados_bloco1 + dados_bloco2)

    @patch("socket.socket")
    def test_get_timeout(self, mock_socket):
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        mock_sock.recvfrom.side_effect = socket.timeout

        # O método retorna False, não levanta exceção
        resultado = self.cliente.get("remoto.txt", "local.txt")
        self.assertFalse(resultado)

    @patch("socket.socket")
    def test_put_success(self, mock_socket):
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        # Simula ACK0 (após WRQ) e ACK1 (após DATA)
        ack0 = b"\x00\x04\x00\x00"
        ack1 = b"\x00\x04\x00\x01"

        # Ordem das respostas: após WRQ -> ACK0; após DATA -> ACK1
        mock_sock.recvfrom.side_effect = [
            (ack0, ("127.0.0.1", 12345)),
            (ack1, ("127.0.0.1", 12345))
        ]

        # Dados do arquivo local: 100 bytes (menor que 512, portanto um único bloco)
        dados_arquivo = b"A" * 100

        with patch("builtins.open", unittest.mock.mock_open(read_data=dados_arquivo)) as mock_file:
            resultado = self.cliente.put("local.txt", "remoto.txt")
            self.assertTrue(resultado)

            # Verifica se ao menos o WRQ e um DATA foram enviados
            self.assertGreaterEqual(mock_sock.sendto.call_count, 2)

    @patch("socket.socket")
    def test_put_file_not_found(self, mock_socket):
        with patch("builtins.open", side_effect=FileNotFoundError):
            resultado = self.cliente.put("naoexiste.txt", "remoto.txt")
            self.assertFalse(resultado)

    @patch("socket.socket")
    def test_put_ack_0_missing(self, mock_socket):
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        # Timeout na resposta após WRQ
        mock_sock.recvfrom.side_effect = socket.timeout

        with patch("builtins.open", unittest.mock.mock_open(read_data=b"dados")):
            resultado = self.cliente.put("local.txt", "remoto.txt")
            self.assertFalse(resultado)