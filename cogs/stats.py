import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.config import Config
from utils.helpers import create_embed
from main import db

logger = logging.getLogger(__name__)

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="stats", description="Ver estatísticas")
    @app_commands.describe(member="Membro para ver stats (opcional)")
    async def stats(self, interaction: discord.Interaction, member: discord.Member = None):
        """Ver estatísticas"""
        
        try:
            if member:
                if not is_admin(interaction.user, Config.ADMIN_ROLE_ID) and member.id != interaction.user.id:
                    embed = create_embed(
                        "❌ Permissão Negada",
                        "Você não pode ver as stats de outro membro",
                        Config.COLOR_ERROR
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                stats = db.get_stats(member.id)
                member_id = member.id
            else:
                stats = db.get_stats()
                member_id = interaction.user.id
            
            if not stats:
                embed = create_embed(
                    "📊 Stats",
                    "Sem dados de estatísticas",
                    Config.COLOR_WARNING
                )
            else:
                embed = create_embed(
                    "📊 Stats",
                    f"Total de ações: {len(stats)}",
                    Config.COLOR_INFO
                )
                
                # Agrupar ações por tipo
                actions = {}
                for stat in stats:
                    stat_id, member_id, action, timestamp = stat
                    if action not in actions:
                        actions[action] = 0
                    actions[action] += 1
                
                for action, count in actions.items():
                    embed.add_field(name=action, value=f"{count}", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Erro ao obter stats: {e}")
            embed = create_embed(
                "❌ Erro",
                f"Erro ao obter stats: {str(e)}",
                Config.COLOR_ERROR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

def is_admin(user: discord.Member, admin_role_id: int) -> bool:
    """Verificar se o usuário é admin"""
    return any(role.id == admin_role_id for role in user.roles)

async def setup(bot):
    await bot.add_cog(StatsCog(bot))
