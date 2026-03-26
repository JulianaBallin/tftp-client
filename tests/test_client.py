import unittest
from unittest.mock import Mock, patch, MagicMock
import socket
import sys
from client import TFTPClient
from tftp_packets import Opcode


class TestTFTPClient(unittest.TestCase):
    def setUp(self):
        self.cliente = TFTPClient("127.0.0.1", 69, timeout=1, max_retries=1)

    @patch("socket.socket")
    def test_get_success(self, mock_socket):
        # Mock do socket
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        # Simula resposta DATA bloco 1 (512 bytes)
        dados_bloco1 = b"X" * 512
        pacote_data = (b"\x00\x03\x00\x01" + dados_bloco1)  # opcode 3, bloco 1
        mock_sock.recvfrom.return_value = (pacote_data, ("127.0.0.1", 12345))

        # Configura arquivo temporário
        with patch("builtins.open", unittest.mock.mock_open()) as mock_file:
            resultado = self.cliente.get("remoto.txt", "local.txt")
            self.assertTrue(resultado)
            mock_file.assert_called_once_with("local.txt", "wb")
            # Verifica se escreveu os dados
            mock_file().write.assert_called_with(dados_bloco1)

    @patch("socket.socket")
    def test_get_timeout(self, mock_socket):
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        mock_sock.recvfrom.side_effect = socket.timeout

        resultado = self.cliente.get("remoto.txt", "local.txt")
        self.assertFalse(resultado)

    @patch("socket.socket")
    def test_put_success(self, mock_socket):
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock

        # Simula ACK do bloco 0
        ack0 = b"\x00\x04\x00\x00"  # opcode 4, bloco 0
        mock_sock.recvfrom.return_value = (ack0, ("127.0.0.1", 12345))

        with patch("builtins.open", unittest.mock.mock_open(read_data=b"dados")) as mock_file:
            resultado = self.cliente.put("local.txt", "remoto.txt")
            self.assertTrue(resultado)

    @patch("socket.socket")
    def test_put_file_not_found(self, mock_socket):
        with patch("builtins.open", side_effect=FileNotFoundError):
            resultado = self.cliente.put("naoexiste.txt", "remoto.txt")
            self.assertFalse(resultado)


if __name__ == "__main__":
    unittest.main()