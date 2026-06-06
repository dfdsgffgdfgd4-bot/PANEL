# 🎮 Irish Lagger Control Panel

Bot Discord para gerenciar o painel de controle do projeto Irish Lagger com sistema de keys, whitelist e blacklist.

## 📋 Funcionalidades

- ✅ Painel interativo com botões
- ✅ Sistema de keys (gerar, validar, resetar HWID)
- ✅ Whitelist e Blacklist de membros
- ✅ Sistema de roles
- ✅ Stats e informações
- ✅ Database SQLite

## 🔧 Requisitos

- Python 3.8+
- discord.py 2.0+
- SQLite3

## 📦 Instalação

```bash
pip install -r requirements.txt
```

## 🚀 Como usar

1. Configure o token do bot em `.env`
2. Execute o bot:

```bash
python main.py
```

## 📝 Comandos

- `/generatekey <member>` - Gerar uma nova key
- `/mykey <project>` - Ver sua key
- `/resethwid <member>` - Resetar HWID
- `/whitelist <member>` - Adicionar à whitelist
- `/blacklist <member>` - Adicionar à blacklist
- `/stats` - Ver estatísticas

## 📂 Estrutura

```
.
├── main.py              # Arquivo principal
├── cogs/
│   ├── panel.py        # Comandos do painel
│   ├── keys.py         # Sistema de keys
│   ├── whitelist.py    # Sistema de whitelist
│   └── stats.py        # Estatísticas
├── db/
│   └── database.py     # Gerenciamento de database
├── utils/
│   ├── config.py       # Configurações
│   └── helpers.py      # Funções auxiliares
├── requirements.txt    # Dependências
└── .env.example        # Exemplo de variáveis de ambiente
```

## 📄 Licença

Privado - Irish Lagger Project
