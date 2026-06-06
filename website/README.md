# 🌐 Irish Lagger Web Panel

Sistema web para download de scripts com autenticação por Key e IP.

## 📋 Funcionalidades

✅ **Autenticação por Key**
- Verificação de keys ativas
- Bloqueio de keys inativas ou revogadas
- Verificação de blacklist

✅ **Gerenciamento de IP**
- Registro de IPs por key
- Limite de 3 IPs por key
- Reset de HWID via Discord bot

✅ **Download de Script**
- Download seguro do script
- Rastreamento de downloads
- Autenticação obrigatória

✅ **Interface Moderna**
- Design responsivo
- Dark mode
- Animações suaves

## 🔧 Instalação

### 1. Instale as dependências:
```bash
pip install -r requirements.txt
```

### 2. Configure o banco de dados:
Certifique-se de que o arquivo `../data/panel.db` existe (criado pelo bot Discord)

### 3. Execute o servidor:
```bash
python app.py
```

O servidor rodará em `http://localhost:5000`

## 🚀 Uso

### Via Browser:
1. Acesse `http://localhost:5000`
2. Digite sua key
3. Clique em "Verificar Key"
4. Registre seu IP (máximo 3)
5. Baixe o script

### Via API:

**Verificar Key:**
```bash
curl -X POST http://localhost:5000/api/check-key \
  -H "Content-Type: application/json" \
  -d '{"key": "ABC123DEF456GHI789"}'
```

**Registrar IP:**
```bash
curl -X POST http://localhost:5000/api/register-ip \
  -H "Content-Type: application/json" \
  -d '{"key": "ABC123DEF456GHI789"}'
```

**Baixar Script:**
```bash
curl -X POST http://localhost:5000/api/download-script \
  -H "Content-Type: application/json" \
  -d '{"key": "ABC123DEF456GHI789"}' \
  -o irish_lagger.exe
```

**Obter Status:**
```bash
curl -X POST http://localhost:5000/api/status \
  -H "Content-Type: application/json" \
  -d '{"key": "ABC123DEF456GHI789"}'
```

## 🔐 Segurança

- ✅ Autenticação obrigatória por key
- ✅ Verificação de blacklist
- ✅ Limite de IPs por key
- ✅ Rastreamento de todos os downloads
- ✅ CORS habilitado para acesso seguro

## 📊 Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Página principal |
| POST | `/api/check-key` | Verificar key |
| POST | `/api/register-ip` | Registrar IP |
| POST | `/api/download-script` | Baixar script |
| POST | `/api/status` | Obter status da key |
| GET | `/api/info` | Informações públicas |

## 📁 Estrutura

```
website/
├── app.py                  # Aplicação Flask principal
├── requirements.txt        # Dependências Python
├── README.md              # Este arquivo
├── templates/
│   └── index.html         # Interface HTML
├── static/
│   ├── css/
│   │   └── style.css      # Estilos CSS
│   └── js/
│       └── script.js      # Lógica JavaScript
└── scripts/
    └── irish_lagger.exe   # Script para download (adicionar manualmente)
```

## 🔗 Integração com Bot Discord

O bot Discord cria as keys que são usadas neste painel web. 

**Comandos do Bot:**
- `/generatekey <member> <project>` - Gerar key
- `/resethwid <member> <key>` - Resetar HWID da key
- `/whitelist <member> add` - Adicionar à whitelist
- `/blacklist <member> add` - Adicionar à blacklist

## ⚙️ Configurações

Edite em `app.py`:

```python
DB_PATH = "../data/panel.db"          # Caminho do banco de dados
MAX_IPS_PER_KEY = 3                   # Limite de IPs por key
SCRIPT_PATH = "./scripts/irish_lagger.exe"  # Caminho do script
```

## 🐛 Troubleshooting

**Erro: "Script não encontrado"**
- Adicione o arquivo `irish_lagger.exe` em `website/scripts/`

**Erro: "Banco de dados não encontrado"**
- Certifique-se de que o bot Discord rodou pelo menos uma vez para criar o banco

**Key inválida**
- Verifique se a key foi gerada corretamente no Discord
- Certifique-se de que a key está ativa (não revogada)

## 📝 Licença

Privado - Irish Lagger Project
