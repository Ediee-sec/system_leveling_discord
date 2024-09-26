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
            user_data = get_data.get_user_data(user_id, server_id, 'timer_message')
            
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
                        ### Fase 1: Ferramentas de Madeira e Pedra (Lv 1-10)
                        ("Martelo de Madeira", 2),
                        ("Martelo de Madeira Duplo", 4),
                        ("Martelo de Pedra", 6),
                        ("Martelo de Pedra Duplo", 8),
                        ("Machado de Metal", 10),

                        ### Fase 2: Ferramentas de Metal (Lv 11-20)
                        ("Machado de Metal Duplo", 12),
                        ("Machado de Prata", 15),
                        ("Machado de Prata Duplo", 18),
                        ("Machado de Ouro", 20),

                        ### Fase 3: Ferramentas Avançadas (Lv 21-40)
                        ("Machado de Ouro Duplo", 23),
                        ("Machado de Metal com Duas Lâminas", 27),
                        ("Machado de Prata com Duas Lâminas", 31),
                        ("Machado de Ouro com Duas Lâminas", 36),

                        ### Fase 4: Estrelas e Conquistas (Lv 41-60)
                        ("Estrela de Bronze", 41),
                        ("Estrela de Prata", 46),
                        ("Estrela de Ouro", 51),
                        ("Duas Estrelas de Ouro", 56),
                        ("Três Estrelas de Ouro", 60),

                        ### Fase 5: Cetros (Lv 61-85)
                        ("Cetro de Violeta", 65),
                        ("Cetro de Safira", 70),
                        ("Cetro de Rubi", 75),
                        ("Cetro de Diamante Negro", 80),
                        ("Cetro de Diamante Puro", 85),

                        ### Fase 6: Medalhas e Conquistas Supremas (Lv 86-100)
                        ("Medalha de Bronze", 90),
                        ("Medalha de Prata", 93),
                        ("Medalha de Ouro", 96),
                        ("Dragão Preto dos Olhos Vermelhos", 100)

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
                xp_for_next_rank = (current_level + 1) * 1024 # Fórmula baseada no próximo rank
                xp_remaining_rank = xp_for_next_rank - current_xp

            # Barra de progresso ajustada para o próximo rank
            progress_rank = int((current_xp / xp_for_next_rank) * 10)  # Dividido por 10 para criar a barra
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
            embed.add_field(name="⚡ **XP Atual**", value=f"**{current_xp:,} / {xp_for_next_rank:,}**", inline=True)

            # Campo de XP Restante para o próximo rank
            embed.add_field(name="🎯 **XP Acumulada**", value=f"**{xp_accumulated:,}**", inline=False)

            # Barra de progresso para o próximo rank
            embed.add_field(name="📈 **Progresso para o Próximo Rank**", value=f"`[{progress_bar_rank}] {current_xp / xp_for_next_rank:.0%}`", inline=False)

            # Responder ao comando com o embed
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"Ocorreu um erro: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RankSlashCommand(bot))
