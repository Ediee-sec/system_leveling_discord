from db import insert_log
from datetime import datetime, timedelta

def get_data_by_user(time, user, type, xp, multiplier, xp_multiplied, level, channel, content):

    time = time.strftime('%d/%m/%Y %H:%M:%S')  # Converte o objeto datetime novamente para uma string '22/09/2024 15:31:32'
    
    dicionarie = {
        'datetime': time,
        'user': user,
        'type': type,
        'xp': xp,
        'multiplier': multiplier,
        'xp_multiplied': xp_multiplied,
        'level': level,
        'channel': channel,
        'content': content
    }
    
    insert_log.insert_user_activity(dicionarie)

    
    
    