<h1 align="center">📡 TFTP Python CLI - Cliente</h1>

<p align="center">
  <img src="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExamN5c3U2ZXprMmk4eWx1M3Zyem9pazBhd2gyOGlqeHV0MHNlYXNwdyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9YEpoKEGPZyVFfRuYm/giphy.gif" width="200">
</p>

<p align="center">
  Cliente TFTP em Python, seguindo a RFC 1350, com interface CLI e arquitetura modular.
  Desenvolvido para disciplina de Tópicos Especiais para Computação I.
</p>

<h2 align="center">📝 Descrição do Projeto</h2>

Este projeto implementa um **cliente TFTP** completo, capaz de realizar downloads (GET) e uploads (PUT) de arquivos. O código segue as especificações da RFC 1350, utilizando UDP, blocos de 512 bytes e confirmações (ACK). A arquitetura é separada em módulos: um para a lógica de transferência e outro para a codificação/decodificação dos pacotes.

O projeto inclui:
- Diagrama de componentes C4 no README e em `docs/diagrams`.
- Testes unitários com `unittest`.
- Interface de linha de comando (CLI) via `argparse`.
- Suporte apenas ao modo **octet** (binário), que é o mais comum.

<h2 align="center">🤖 Tecnologias Utilizadas</h2>

<p align="center">
  <a href="https://www.python.org"><img alt="Python" src="https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python"></a>
  <a href="https://docs.python.org/3/library/unittest.html"><img alt="Unittest" src="https://img.shields.io/badge/unittest-✔-green?style=for-the-badge"></a>
  <a href="https://www.python.org/dev/peps/pep-0008/"><img alt="PEP 8" src="https://img.shields.io/badge/PEP%208-✔-yellow?style=for-the-badge"></a>
  <a href="https://git-scm.com/"><img alt="Git" src="https://img.shields.io/badge/git-✔-orange?style=for-the-badge&logo=git"></a>
</p>

<h2 align="center">📁 Estrutura do Projeto</h2>

```bash
📦 tftp-client
├── 📄 client.py # Lógica principal do cliente
├── 📄 tftp_packets.py # Codificação/decodificação de pacotes
├── 📄 logger.py # Logs coloridos
├── 📄 exceptions.py # Exceções personalizadas
├── 📄 cli.py # CLI e menu interativo
├── 📄 main.py # Ponto de entrada (modo automático)
├── 📄 requirements.txt # Dependências
├── 📄 LICENSE # MIT
├── 📄 README.md
├── 📁 tests/ # Testes unitários
└── 📁 docs/diagrams/ # Diagramas C4
```

<h1 align="center">🧩 Diagrama C4 – Cliente TFTP</h1>

```mermaid
C4Component
    title Diagrama de Componentes do Cliente TFTP

    Container_Boundary(client_app, "TFTP Client App") {
        Component(cli_client, "CLI do Cliente", "Python/Argparse", "Interface de linha de comando.")
        Component(client_core, "Client Core", "Python/Socket", "Gerencia o fluxo de transferência.")
    }

    Component(packets, "Protocol Encoder/Decoder", "Python/Struct", "Codifica e decodifica pacotes.")
    Component(errors, "Error Handling", "Python/Enum", "Códigos e mensagens de erro.")

    Rel(cli_client, client_core, "Usa")
    Rel(client_core, packets, "Usa")
    Rel(client_core, errors, "Usa")

    System_Ext(server, "Servidor TFTP", "Qualquer servidor que siga a RFC 1350")
    Rel(client_core, server, "UDP", "porta 69 ou efêmera")
```

<p align="center">
  <img src="docs/diagrams/03_componentes_cliente.png" alt="Diagrama de Componentes" width="600">
</p>

<h1 align="center">🚀 Como Executar</h1>

### Instalação
```bash
git clone https://github.com/JulianaBallin/tftp-client.git
cd tftp-client
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Download (GET)
```bash
python client.py get --host 127.0.0.1 --port 69 --remote arquivo.txt --local destino.txt
```

### Upload (PUT)
```bash
python client.py put --host 127.0.0.1 --port 69 --local local.txt --remote remoto.txt
```

<h2 align="center">🧪 Testes</h2>

```bash
# Executar testes unitários
python -m unittest discover tests

# Com cobertura (se pytest instalado)
pytest tests/ --cov=. --cov-report=term
```

<h2 align="center">📚 Referências</h2>

- [RFC 1350 – TFTP](https://datatracker.ietf.org/doc/html/rfc1350)
- [Git Pull Request](https://www.geeksforgeeks.org/git/git-pull-request/)
- [PEP 8 – Style Guide](https://www.python.org/dev/peps/pep-0008/)

<h2 align="center">👥 Equipe</h2>

| Nome | Matrícula |
|------|-----------|
| Juliana Ballin Lima | 2315310011 |
| João Lucas Noronha de Castro | 2315310009 |
| Leonardo Castro da Silva | 2215310016 |
| Leonardo Melo Crispim | 2315310036 |
| Lucas Carvalho dos Santos | 2315310012 |
| Renato Barbosa de Carvalho | 2315310021 |
| Vinicius Souza Costa | 2315310024 |

---

<h3 align="center">MIT © Equipe 4 – UEA</h3>
