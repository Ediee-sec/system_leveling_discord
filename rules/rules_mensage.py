import discord
from discord.ext import commands
import random
import time
from datetime import datetime, timezone, timedelta
from discord import ChannelType
from db import get_data, update
from img import top
import emoji
import re

class RulesMensage:
    def __init__(self):

        self.CUSTOM_EMOJI_PATTERN = r'<a?:\w+:\d+>'

        
    def check_rules_message(self, mensage, last_message_time):
        """
        Checa se a mensagem enviada pelo usuário segue as regras para ganhar XP.

        - Se a mensagem for enviada por um bot
        - Se a mensagem for enviada em um canal de voz ou chat de canal de voz
        - Se a mensagem contiver emojis customizados
        - Se a mensagem contiver emojis padrão do discord
        - Se a mensagem contiver imagens
        - Se a mensagem for igual a mensagem enviada anteriormente

        Se a mensagem não atender a essas regras, retorna True, caso contr rio, retorna False.
        """
        if mensage.author.bot or \
        mensage.channel.type == ChannelType.voice or \
        mensage.channel.type == ChannelType.stage_voice or \
        any(isinstance(part, discord.Emoji) for part in mensage.content) or \
        any(char in emoji.EMOJI_DATA for char in mensage.content) or \
        re.search(self.CUSTOM_EMOJI_PATTERN, mensage.content) or \
        len(mensage.attachments) >= 1 or \
        mensage.content == last_message_time:
            return True
        
    def check_rules_voice(self):
        pass
            
         