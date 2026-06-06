import discord
from discord.ext import commands
from discord import app_commands
import logging
from utils.config import Config
from utils.helpers import create_embed, generate_key, is_admin
from main import db

logger = logging.getLogger(__name__)

class KeysCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="generatekey", description="Gerar uma nova key para um membro")
    @app_commands.describe(member="Membro para gerar a key", project="Projeto da key")
    @app_commands.checks.has_role(Config.ADMIN_ROLE_ID)
    async def generatekey(self, interaction: discord.Interaction, member: discord.Member, project: str = "Irish Lagger"):
        """Gerar uma nova key"""
        
        try:
            key_code = generate_key()
            
            # Salvar no banco de dados
            if db.create_key(key_code, project, member.id):
                embed = create_embed(
                    "✅ Key Gerada",
                    f"Uma nova key foi gerada para {member.mention}",
                    Config.COLOR_SUCCESS,
                    **{
                        "Key": f"```{key_code}```",
                        "Projeto": project,
                        "Membro": member.mention
                    }
                )
                
                await interaction.response.send_message(embed=embed)
                
                # Enviar DM para o membro
                try:
                    dm_embed = create_embed(
                        "🔑 Sua Key",
                        f"Você recebeu uma nova key para o projeto {project}!",
                        Config.COLOR_INFO,
                        **{"Key": f"```{key_code}```"}
                    )
                    await member.send(embed=dm_embed)
                except:
                    logger.warning(f"Não foi possível enviar DM para {member}")
                
                db.add_stat(member.id, f"Key gerada - {project}")
                logger.info(f"Key gerada para {member} - {key_code}")
            else:
                embed = create_embed(
                    "❌ Erro",
                    "Houve um erro ao gerar a key.",
                    Config.COLOR_ERROR
                )
                await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            logger.error(f"Erro ao gerar key: {e}")
            embed = create_embed(
                "❌ Erro",
                f"Erro ao gerar key: {str(e)}",
                Config.COLOR_ERROR
            )
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="mykey", description="Ver sua key")
    @app_commands.describe(project="Projeto para ver a key")
    async def mykey(self, interaction: discord.Interaction, project: str = "Irish Lagger"):
        """Ver sua key"""
        
        try:
            keys = db.get_member_keys(interaction.user.id)
            
            if not keys:
                embed = create_embed(
                    "❌ Sem Keys",
                    f"Você não tem nenhuma key registrada.",
                    Config.COLOR_WARNING
                )
            else:
                embed = create_embed(
                    "🔑 Suas Keys",
                    f"Aqui estão suas keys registradas:",
                    Config.COLOR_INFO
                )
                
                for key in keys:
                    key_id, key_code, member_id, key_project, hwid, status, created_at, used_at, reset_count = key
                    embed.add_field(
                        name=f"Projeto: {key_project}",
                        value=f"```{key_code}```\nStatus: {status}",
                        inline=False
                    )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            db.add_stat(interaction.user.id, "Visualizou suas keys")
        
        except Exception as e:
            logger.error(f"Erro ao obter keys: {e}")
            embed = create_embed(
                "❌ Erro",
                f"Erro ao obter keys: {str(e)}",
                Config.COLOR_ERROR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="resethwid", description="Resetar HWID de uma key")
    @app_commands.describe(member="Membro para resetar HWID", key="Código da key")
    @app_commands.checks.has_role(Config.ADMIN_ROLE_ID)
    async def resethwid(self, interaction: discord.Interaction, member: discord.Member = None, key: str = None):
        """Resetar HWID de uma key"""
        
        try:
            if key and db.reset_hwid(key):
                embed = create_embed(
                    "✅ HWID Resetado",
                    f"O HWID da key foi resetado com sucesso.",
                    Config.COLOR_SUCCESS
                )
                await interaction.response.send_message(embed=embed)
                
                if member:
                    db.add_stat(member.id, "HWID resetado")
                logger.info(f"HWID resetado para {key}")
            else:
                embed = create_embed(
                    "❌ Erro",
                    f"Key não encontrada ou erro ao resetar.",
                    Config.COLOR_ERROR
                )
                await interaction.response.send_message(embed=embed)
        
        except Exception as e:
            logger.error(f"Erro ao resetar HWID: {e}")
            embed = create_embed(
                "❌ Erro",
                f"Erro ao resetar HWID: {str(e)}",
                Config.COLOR_ERROR
            )
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(KeysCog(bot))
