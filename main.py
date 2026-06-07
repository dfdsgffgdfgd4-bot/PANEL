import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
from utils.database import Database

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Criar bot
bot = commands.Bot(command_prefix="/", intents=intents)

# Variável global para database
db = None

@bot.event
async def on_ready():
    global db
    logger.info(f"Bot conectado como {bot.user}")
    logger.info(f"Bot está em {len(bot.guilds)} servidor(es)")
    
    # Sincronizar comandos slash
    try:
        synced = await bot.tree.sync()
        logger.info(f"{len(synced)} comando(s) sincronizado(s)")
    except Exception as e:
        logger.error(f"Erro ao sincronizar comandos: {e}")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f"Erro em {event}: {args} {kwargs}", exc_info=True)

async def load_cogs():
    """Carregar todos os cogs"""
    cogs_dir = "cogs"
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"✅ Cog {filename} carregado")
            except Exception as e:
                logger.error(f"❌ Erro ao carregar {filename}: {e}")

async def main():
    global db
    
    # Inicializar database
    db = Database()
    db.init_db()
    logger.info("✅ Database inicializado")
    
    # Carregar cogs
    await load_cogs()
    
    # Conectar bot
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("❌ DISCORD_TOKEN não encontrado em .env")
        return
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot desligado pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao iniciar bot: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
