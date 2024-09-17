import discord
from discord.ext import commands
import random
import time
from datetime import datetime, timezone, timedelta
from discord import ChannelType
from db import get_data, update
from img import top

def calculate_xp(level):
    return 1024 * level

class XPMensage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_rank_id = 1284961905621991585
        self.server_booster_multiplier = 1.5
        self.timer = 60
        self.xp = random.randint(50, 55)  # XP aleatório definido aqui
        super().__init__()

    async def update_user_role(self, member, new_level):
        guild = member.guild
        roles_dict = {
            2: "Martelo de Madeira",
            6: "Machado de Metal",
            12: "Machado de Prata",
            20: "Machado de Prata Duplo",
            30: "Machado de Ouro",
            45: "Machado de Batalha de Metal",
            70: "Cetro de Safira",
            100: "Cetro de Diamante",
            200: "Dragão Preto de olhos Vermelhos"
        }

        # Pega os nomes dos cargos
        new_role_name = None
        for level, role_name in sorted(roles_dict.items(), reverse=True):
            if new_level >= level:
                new_role_name = role_name
                break

        if new_role_name:
            role_to_add = discord.utils.get(guild.roles, name=new_role_name)

            # Remove todos os outros cargos da lista
            for level, role_name in roles_dict.items():
                role_to_remove = discord.utils.get(guild.roles, name=role_name)
                if role_to_remove in member.roles and role_to_remove != role_to_add:
                    await member.remove_roles(role_to_remove)

            # Adiciona o novo cargo
            if role_to_add not in member.roles:
                await member.add_roles(role_to_add)

                elo = top.top(new_role_name)

                channel_id = self.channel_rank_id
                channel = self.bot.get_channel(channel_id)
                if channel:
                    try:
                        await channel.send(f"Parabéns {member.mention}, você subiu para o rank **{new_role_name}** {elo}!")
                    except Exception as e:
                        print(f"Erro ao enviar mensagem: {e}")
                else:
                    print(f"Canal com ID {channel_id} não encontrado.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # Ignorar mensagens de bots
        
        # Verificar se a mensagem foi enviada em um canal de voz ou chat de canal de voz
        if message.channel.type == ChannelType.voice or message.channel.type == ChannelType.stage_voice:
            return  # Não conceder XP em canais de voz

        user_id = message.author.id
        user_name = message.author.name
        avatar_url = str(message.author.avatar.url) if message.author.avatar.url else 'https://i.ibb.co/xYxjFvw/9c3bb649-9038-4113-9543-7c87652aa95a-removebg-preview.png'  # URL da imagem do perfil
        server_id = message.guild.id  # ID do servidor
        current_time = datetime.now(timezone.utc)  # Tempo atual em segundos

        # Buscar dados do usuário no banco de dados
        user_data = get_data.get_user_data(user_id, server_id)
        if not user_data:
            user_data = {'img': avatar_url, 'user_dc': user_name, 'xp': 0, 'xp_accumulated': 0, 'lvl': 1, 'timer': 0, 'server_id': server_id, 'last_message': ''}
            
        if message.content == user_data['last_message']:
            return  # Ignorar se a mensagem é igual à anterior

        # Atualiza o conteúdo da última mensagem enviada pelo usuário
        user_data['last_message'] = message.content

        # Verificar se o cooldown de 1 minuto (60 segundos) já passou
        last_xp_time = user_data['timer']
        if last_xp_time == 0:
            last_xp_time = datetime.now(timezone.utc) - timedelta(seconds=60)

        if last_xp_time.tzinfo is None:  # Se last_xp_time não tiver informações de fuso horário, adicionar UTC
            last_xp_time = last_xp_time.replace(tzinfo=timezone.utc)

        # Verificar se o cooldown de 1 minuto (60 segundos) já passou
        time_diff = current_time - last_xp_time
        if time_diff.total_seconds() < self.timer:
            return  # Se não passou 1 minuto, não dá XP

        # Verificar se o usuário é Server Booster
        is_booster = any(role.name == 'Server Booster' for role in message.author.roles)

        # Adiciona XP aleatório entre 5 e 15 por mensagem
        xp_to_add = self.xp

        # Aplicar o multiplicador de 15% se o usuário for Server Booster
        xp_multiplier = self.server_booster_multiplier if is_booster else 1.0
        xp_to_add = int(xp_to_add * xp_multiplier)

        user_data['xp'] += xp_to_add
        user_data['xp_accumulated'] += xp_to_add
        user_data['timer'] = current_time  # Atualiza o tempo da última vez que ganhou XP

        # Verifica se o usuário deve subir de nível
        current_level = user_data['lvl']
        xp_for_next_level = calculate_xp(current_level)

        if user_data['xp'] >= xp_for_next_level:
            user_data['lvl'] += 1
            user_data['xp'] -= xp_for_next_level
            channel_rank = self.bot.get_channel(self.channel_rank_id)

            await self.update_user_role(message.author, user_data['lvl'])

        # Salvar os dados no banco de dados
        update.upsert_user_data(user_id, avatar_url, user_name, user_data['xp'], user_data['xp_accumulated'], user_data['lvl'], user_data['timer'], server_id, message.content)

        # Processar os comandos do bot (necessário para o on_message)
        await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(XPMensage(bot))
