from discord.ext import commands, tasks
import discord
import random
import time
from datetime import datetime, timezone
from db import get_data, update
from img import top
from log import logger
import pytz

def calculate_xp(level):
    return 1024 * level

class XPVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp = random.randint(80, 90)
        self.server_booster_multiplier = 1.15
        self.give_voice_xp.start()  # Inicia o loop de tarefas
    
    async def update_user_role(self, member, new_level):
        guild = member.guild
        roles_dict = {
                        # Fase 1: Ferramentas de Madeira e Pedra (Lv 1-9)
                        2: "Martelo de Madeira",
                        4: "Martelo de Madeira Duplo",
                        6: "Martelo de Pedra",
                        8: "Martelo de Pedra Duplo",
                        
                        # Fase 2: Ferramentas de Metal (Lv 10-19)
                        10: "Machado de Metal",
                        12: "Machado de Metal Duplo",
                        15: "Machado de Prata",
                        18: "Machado de Prata Duplo",
                        
                        # Fase 3: Ferramentas Avançadas (Lv 20-40)
                        20: "Machado de Ouro",
                        23: "Machado de Ouro Duplo",
                        27: "Machado de Metal Com Duas Lâminas",
                        31: "Machado de Prata Com Duas Lâminas",
                        36: "Machado de Ouro Com Duas Lâminas",
                        
                        # Fase 4: Estrelas e Conquistas (Lv 41-60)
                        41: "Estrela de Bronze",
                        46: "Estrela de Prata",
                        51: "Estrela de Ouro",
                        56: "Duas Estrelas de Ouro",
                        60: "Três Estrelas de Ouro",
                        
                        # Fase 5: Cetros (Lv 61-85)
                        65: "Cetro de Violeta",
                        70: "Cetro de Safira",
                        75: "Cetro de Rubi",
                        80: "Cetro de Diamante Negro",
                        85: "Cetro de Diamante Puro",
                        
                        # Fase 6: Medalhas e Conquista Supremas (Lv 86-100)
                        90: "Medalha de Bronze",
                        93: "Medalha de Prata",
                        96: "Medalha de Ouro",
                        100: "Dragão Preto dos Olhos Vermelhos"

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
                    user_data = get_data.get_user_data(user_id, server_id, 'timer_voice')
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
                    #xp_to_add = self.xp
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
                    current_time = datetime.now(timezone.utc)  # Tempo atual em segundos
                    sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
                    current_time = current_time.astimezone(sao_paulo_tz)
                    user_data['timer_voice'] = current_time
                    
                    logger.get_data_by_user(current_time, member.name, 'Voice', self.xp, xp_multiplier, xp_to_add, user_data['lvl'],member.voice.channel.name, None)

                    # Salvar os dados no banco de dados
                    update.upsert_user_data(user_id, user_data['img'], user_data['user_dc'], user_data['xp'],user_data['xp_accumulated'], user_data['lvl'], current_time, server_id, user_data['last_message'], 'timer_voice')

    @give_voice_xp.before_loop
    async def before_give_voice_xp(self):
        await self.bot.wait_until_ready()
        
async def setup(bot):
    await bot.add_cog(XPVoice(bot)) 