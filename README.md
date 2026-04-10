# PySimpleGUI_Sistema_Senhas

Projeto simples para gerenciamento de senhas com interface PySimpleGUI e armazenamento em SQLite.

**Requisitos**

- Python 3.10+ (virtualenv recomendado)
- Dependências listadas em `requirements.txt`

**Instalação (Windows)**

1. Clone o repositório e entre na pasta do projeto.
2. Crie e ative um ambiente virtual:

```powershell
python -m venv venv
& venv\Scripts\Activate.ps1
```

1. Instale dependências:

```powershell
python -m pip install -r requirements.txt
```

**Chave AES (obrigatória)**
O projeto usa uma chave AES definida na variável de ambiente `AES_KEY` (hex). Gere uma chave com o utilitário incluso:

```powershell
python generate_key.py
# copia a saída (hex) e crie um arquivo .env com:
# AES_KEY=<hex_gerado>
```

Exemplo de `.env`:

```
AES_KEY=0123ab...ef
```

O pacote `python-dotenv` carrega automaticamente o `.env`.

**Executar**
Depois de ativar o venv e criar `.env`, rode:

```powershell
python main.py
```

Isso inicializa o banco (`banco_dados.db`) e abre a interface.

**Estrutura principal**

- `main.py` — inicia o banco e a GUI
- `generate_key.py` — gera chave AES (hex)
- `config/database.py` — inicialização do SQLite
- `layouts/` — telas PySimpleGUI
- `controllers/` — lógica de acesso ao banco
- `services/` — serviço de criptografia

**Segurança**

- Senhas são criptografadas com AES-256 antes de salvar.
- A chave AES é lida de variável de ambiente, não hardcoded.
- O banco de dados é local e não exposto a redes.

## Aviso de Segurança

### Este repositório é para fins educacionais e não deve ser usado em produção para armazenar senhas reais.
