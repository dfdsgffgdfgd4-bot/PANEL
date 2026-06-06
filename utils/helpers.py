import discord
import secrets
import string
from typing import Optional

def generate_key(length: int = 32) -> str:
    """Gerar uma key aleatória"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def create_embed(title: str, description: str = "", color: int = 0x0000FF, **fields) -> discord.Embed:
    """Criar um embed padrão"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    
    for field_name, field_value in fields.items():
        embed.add_field(name=field_name, value=field_value, inline=False)
    
    return embed

def is_admin(user: discord.Member, admin_role_id: int) -> bool:
    """Verificar se o usuário é admin"""
    return any(role.id == admin_role_id for role in user.roles)
