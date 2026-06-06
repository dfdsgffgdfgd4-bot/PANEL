import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.config import Config
from utils.helpers import create_embed
from main import db

logger = logging.getLogger(__name__)

class BlacklistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="blacklist", description="Gerenciar blacklist")
    @app_commands.describe(member="Membro para adicionar/remover", action="Ação: add ou remove", reason="Razão")
    @app_commands.checks.has_role(Config.ADMIN_ROLE_ID)
    async def blacklist(self, interaction: discord.Interaction, member: discord.Member, action: str = "add", reason: str = "Sem razão"):
        """Gerenciar blacklist"""
        
        try:
            if action.lower() == "add":
                if db.add_blacklist(member.id, interaction.user.id, reason):
                    embed = create_embed(
                        "✅ Adicionado à Blacklist",
                        f"{member.mention} foi adicionado à blacklist",
                        Config.COLOR_ERROR,
                        **{"Razão": reason}
                    )
                    await interaction.response.send_message(embed=embed)
                    db.add_stat(member.id, "Adicionado à blacklist")
                    logger.info(f"{member} adicionado à blacklist por {interaction.user}")
                else:
                    embed = create_embed(
                        "⚠️ Aviso",
                        f"{member.mention} já está na blacklist",
                        Config.COLOR_WARNING
                    )
                    await interaction.response.send_message(embed=embed)
            
            elif action.lower() == "remove":
                if db.remove_blacklist(member.id):
                    embed = create_embed(
                        "✅ Removido da Blacklist",
                        f"{member.mention} foi removido da blacklist",
                        Config.COLOR_SUCCESS
                    )
                    await interaction.response.send_message(embed=embed)
                    db.add_stat(member.id, "Removido da blacklist")
                    logger.info(f"{member} removido da blacklist por {interaction.user}")
                else:
                    embed = create_embed(
                        "❌ Erro",
                        f"{member.mention} não está na blacklist",
                        Config.COLOR_ERROR
                    )
                    await interaction.response.send_message(embed=embed)
            
            else:
                embed = create_embed(
                    "❌ Erro",
                    "Ação inválida. Use 'add' ou 'remove'",
                    Config.COLOR_ERROR
                )
                await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            logger.error(f"Erro ao gerenciar blacklist: {e}")
            embed = create_embed(
                "❌ Erro",
                f"Erro ao gerenciar blacklist: {str(e)}",
                Config.COLOR_ERROR
            )
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="checkblacklist", description="Verificar se um membro está na blacklist")
    @app_commands.describe(member="Membro para verificar")
    async def checkblacklist(self, interaction: discord.Interaction, member: discord.Member):
        """Verificar blacklist"""
        
        try:
            is_blacklisted = db.is_blacklisted(member.id)
            
            if is_blacklisted:
                embed = create_embed(
                    "❌ Blacklisted",
                    f"{member.mention} está na blacklist",
                    Config.COLOR_ERROR
                )
            else:
                embed = create_embed(
                    "✅ Não Blacklisted",
                    f"{member.mention} NÃO está na blacklist",
                    Config.COLOR_SUCCESS
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Erro ao verificar blacklist: {e}")
            embed = create_embed(
                "❌ Erro",
                f"Erro ao verificar blacklist: {str(e)}",
                Config.COLOR_ERROR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(BlacklistCog(bot))
