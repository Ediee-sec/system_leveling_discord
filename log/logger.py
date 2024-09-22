from db import insert_log
from datetime import datetime, timedelta

def get_data_by_user(time, user, type, xp, multiplier, xp_multiplied, level, channel, content):
    # Supondo que 'time' esteja em um formato como 'YYYY-MM-DD HH:MM:SS'
    time_format = '%d/%m/%Y %H:%M:%S'  # Formato para '22/09/2024 15:31:32'
    time = datetime.strptime(time, time_format)  # Converte a string 'time' para um objeto datetime
    time = time - timedelta(hours=3)  # Subtrai 3 horas do objeto datetime
    time = time.strftime(time_format)  # Converte o objeto datetime novamente para uma string '22/09/2024 15:31:32'
    
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

    
    
    