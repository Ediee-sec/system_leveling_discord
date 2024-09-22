from discord.ext import commands, tasks
import discord
import random
import time
from datetime import datetime, timezone
from db import get_data, update
from img import top

def calculate_xp(level):
    return 1024 * level

class XPVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp = random.randint(40, 45)
        self.server_booster_multiplier = 1.75
        self.give_voice_xp.start()  # Inicia o loop de tarefas
    
    async def update_user_role(self, member, new_level):
        guild = member.guild
        roles_dict = {
            2: "Martelo de Madeira",
            4: "Martelo de Madeira Duplo",
            7: "Martelo de Pedra",
            9: "Martelo de Pedra Duplo",
            12: "Machado de Metal",
            14: "Machado de Metal Duplo",
            20: "Machado de Prata",
            24: "Machado de Prata Duplo",
            32: "Machado de Ouro",
            35: "Machado de Ouro Duplo",
            40: "Machado de Metal com Duas Lâminas",
            45: "Machado de Prata com Duas Lâminas",
            50: "Machado de Ouro com Duas Lâminas",
            60: "Cetro de Violeta",
            70: "Cetro de Safira",
            80: "Cetro de Ruby",
            100: "Cetro de Diamante Negro",
            120: "Cetro de Diamante Negro",
            150: "Dragão Ambar",
            200: "Dragão Preto dos olhos Vermelhos"
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
            
                channel_id = 1284961905621991585  # Substitua com o ID correto do canal de texto
                channel = self.bot.get_channel(channel_id)
                if channel:
                    try:
                        await channel.send(f"Parabéns {member.mention}, você subiu para o rank **{new_role_name}** {elo}!")
                    except Exception as e:
                        print(f"Erro ao enviar mensagem: {e}")
                else:
                    print(f"Canal com ID {channel_id} não encontrado.")
    
    @tasks.loop(seconds=300)  
    async def give_voice_xp(self):
        for guild in self.bot.guilds:
            ignore_channel_id = 1033503431773671504  # ID do canal a ser ignorado
            for member in guild.members:
                if member.voice and not member.voice.self_mute:
                    if member.voice.channel.id == ignore_channel_id:
                        continue
                    
                    # Verificar o número de membros na mesma sala de voz
                    voice_channel = member.voice.channel
                    if len(voice_channel.members) < 2:  # Considera o próprio membro, então precisa de pelo menos 4 na sala
                        continue  # Não concede XP se houver menos de 3 membros na sala
                    
                    user_id = member.id
                    server_id = guild.id
                    avatar_url = str(member.avatar.url) if member.avatar else 'https://i.ibb.co/xYxjFvw/9c3bb649-9038-4113-9543-7c87652aa95a-removebg-preview.png'
                    user_data = get_data.get_user_data(user_id, server_id)
                    if not user_data:
                        user_data = {'img': avatar_url, 'user_dc': member.name, 'xp': 0,'xp_accumulated': 0, 'lvl': 1, 'timer': 0, 'server_id': server_id, 'last_message': ''}

                     # Verificar se o usuário é Server Booster
                    is_booster = any(role.name == 'Server Booster' for role in member.roles)

                    # Adiciona XP aleatório entre 5 e 15 por mensagem
                    xp_to_add = self.xp

                    # Aplicar o multiplicador de 15% se o usuário for Server Booster
                    xp_multiplier = self.server_booster_multiplier if is_booster else 1.0
                    xp_to_add = int(xp_to_add * xp_multiplier)
                                
                    # Adiciona XP aleatório entre 20 e 30 por minuto
                    xp_to_add = self.xp
                    user_data['xp'] += xp_to_add
                    user_data['xp_accumulated'] += xp_to_add

                    # Verifica se o usuário deve subir de nível
                    current_level = user_data['lvl']
                    xp_for_next_level = calculate_xp(current_level)

                    if user_data['xp'] >= xp_for_next_level:
                        user_data['lvl'] += 1
                        user_data['xp'] -= xp_for_next_level
                        
                        await self.update_user_role(member, user_data['lvl'])

                    # Atualiza o timer
                    user_data['timer_voice'] = datetime.now(timezone.utc)

                    # Salvar os dados no banco de dados
                    update.upsert_user_data(user_id, user_data['img'], user_data['user_dc'], user_data['xp'],user_data['xp_accumulated'], user_data['lvl'], user_data['timer'], server_id, user_data['last_message'])

    @give_voice_xp.before_loop
    async def before_give_voice_xp(self):
        await self.bot.wait_until_ready()
        
async def setup(bot):
    await bot.add_cog(XPVoice(bot)) 