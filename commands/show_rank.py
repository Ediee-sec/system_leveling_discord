import discord
from discord import app_commands
from discord.ext import commands
from db import get_data

class RankSlashCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rank", description="Veja seu rank atual")
    async def rank(self, interaction: discord.Interaction):
        try:
            # Defere a resposta imediatamente para evitar timeout
            await interaction.response.defer()  
            
            # Obter dados do usuário
            user_id = interaction.user.id
            server_id = interaction.guild.id
            user_data = get_data.get_user_data(user_id, server_id)
            
            if not user_data:
                await interaction.followup.send("Você ainda não tem um rank!", ephemeral=True)
                return

            # Dados do usuário
            avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
            current_level = user_data['lvl']
            xp_accumulated = user_data['xp_accumulated']
            current_xp = user_data['xp']
            xp_for_next_level = 1024 * current_level  # Fórmula para calcular XP necessário para o próximo nível
            xp_remaining = xp_for_next_level - current_xp

            # Definindo os ranks e seus requisitos de nível
            ranks = [
                ("Lenda", 150),
                ("Mestre", 80),
                ("Diamante", 50),
                ("Platina", 30),
                ("Ouro", 18),
                ("Prata", 12),
                ("Bronze", 6),
                ("Madeira", 2)
            ]

            # Função para calcular o rank atual com base no nível
            def get_current_rank(level):
                for rank, lvl_required in ranks:
                    if level >= lvl_required:
                        return rank, lvl_required
                return "Iniciante", 1  # Caso esteja abaixo do nível 2

            # Obter o rank atual e o nível necessário para o próximo rank
            current_rank, rank_level = get_current_rank(current_level)

            # Encontrar o próximo rank
            next_rank = None
            next_rank_level = None
            for rank, lvl_required in reversed(ranks):
                if current_level < lvl_required:
                    next_rank = rank
                    next_rank_level = lvl_required
                    break

            # Se o jogador já estiver no rank mais alto (Lenda)
            if next_rank is None:
                next_rank = "Máximo"
                xp_for_next_rank = xp_accumulated  # Já no nível máximo
                xp_remaining_rank = 0
            else:
                xp_for_next_rank = 1024 * (next_rank_level - 1)  # Fórmula baseada no próximo rank
                xp_remaining_rank = xp_for_next_rank - xp_accumulated

            # Barra de progresso ajustada para o próximo rank
            progress_rank = int((xp_accumulated / xp_for_next_rank) * 10)  # Dividido por 10 para criar a barra
            progress_bar_rank = "█" * progress_rank + "░" * (10 - progress_rank)

            # Criar a mensagem de resposta com embed
            embed = discord.Embed(title="🏅 Seu Rank Atual", color=discord.Color.blue())
            embed.set_thumbnail(url=avatar_url)

            # Rank atual e próximo rank
            embed.add_field(name="🔰 **Rank Atual**", value=f"**{current_rank}**", inline=False)
            if next_rank != "Máximo":
                embed.add_field(name="🎯 **Próximo Rank**", value=f"**{next_rank}** (Nível {next_rank_level})", inline=False)
            else:
                embed.add_field(name="🎯 **Próximo Rank**", value=f"**Você alcançou o rank máximo!**", inline=False)

            # Campo de Nível
            embed.add_field(name="🔰 **Nível**", value=f"**{current_level}**", inline=True)

            # Campo de XP Atual com barra de progresso para o próximo rank
            embed.add_field(name="⚡ **XP Atual**", value=f"**{xp_accumulated:,} / {xp_for_next_rank:,}**", inline=True)

            # Campo de XP Restante para o próximo rank
            embed.add_field(name="🎯 **XP Restante para o Próximo Rank**", value=f"**{xp_remaining_rank:,}**", inline=False)

            # Barra de progresso para o próximo rank
            embed.add_field(name="📈 **Progresso para o Próximo Rank**", value=f"`[{progress_bar_rank}] {xp_accumulated / xp_for_next_rank:.0%}`", inline=False)

            # Responder ao comando com o embed
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"Ocorreu um erro: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RankSlashCommand(bot))
