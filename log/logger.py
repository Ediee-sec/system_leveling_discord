from db import insert_log
from datetime import datetime, timedelta

def get_data_by_user(time, user, type, xp, multiplier, xp_multiplied, level, channel, content):
    # Supondo que 'time' esteja em um formato como 'YYYY-MM-DD HH:MM:SS'
    time_format = '%Y-%m-%d %H:%M:%S'  # Altere este formato conforme a estrutura de sua string de tempo
    time = datetime.strptime(time, time_format)  # Converte a string 'time' para um objeto datetime
    time = time - timedelta(hours=3)  # Subtrai 3 horas do objeto datetime
    
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

    
    
    