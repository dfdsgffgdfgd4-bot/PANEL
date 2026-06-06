import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.config import Config
from utils.helpers import create_embed

logger = logging.getLogger(__name__)

class PanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="panel", description="Mostrar o painel de controle")
    @app_commands.checks.has_role(Config.ADMIN_ROLE_ID)
    async def panel(self, interaction: discord.Interaction):
        """Criar o painel interativo"""
        
        embed = discord.Embed(
            title="🎮 Irish Lagger Control Panel",
            description="Este é o painel de controle do projeto Irish Lagger.\n\nSe você é um comprador, clique nos botões abaixo para resgatar sua key, obter o script ou obter seu role.",
            color=Config.COLOR_INFO
        )
        
        embed.add_field(
            name="📝 Comandos Disponíveis",
            value="`/generatekey` - Gerar uma nova key\n"
                  "`/mykey` - Ver sua key\n"
                  "`/resethwid` - Resetar HWID\n"
                  "`/whitelist` - Adicionar à whitelist\n"
                  "`/blacklist` - Adicionar à blacklist\n"
                  "`/stats` - Ver estatísticas",
            inline=False
        )
        
        # Criar botões
        view = PanelView()
        
        await interaction.response.send_message(embed=embed, view=view)
        logger.info(f"Painel criado por {interaction.user}")

class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🔑 Redeem Key", style=discord.ButtonStyle.green, custom_id="btn_redeem")
    async def redeem_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_embed(
            "🔑 Redeem Key",
            "Para resgatar sua key, use o comando `/mykey <projeto>`",
            Config.COLOR_INFO
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📜 Get Script", style=discord.ButtonStyle.primary, custom_id="btn_script")
    async def script_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_embed(
            "📜 Get Script",
            "Entre em contato com um administrador para obter o script.",
            Config.COLOR_INFO
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="👤 Get Role", style=discord.ButtonStyle.blurple, custom_id="btn_role")
    async def role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_embed(
            "👤 Get Role",
            "Use o comando `/generatekey` para obter uma role.",
            Config.COLOR_INFO
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="⚙️ Reset HWID", style=discord.ButtonStyle.secondary, custom_id="btn_reset")
    async def reset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_embed(
            "⚙️ Reset HWID",
            "Use o comando `/resethwid <membro>` para resetar o HWID.",
            Config.COLOR_INFO
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📊 Get Stats", style=discord.ButtonStyle.primary, custom_id="btn_stats")
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_embed(
            "📊 Stats",
            "Use o comando `/stats` para ver as estatísticas.",
            Config.COLOR_INFO
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(PanelCog(bot))
