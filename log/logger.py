from db import insert_log
from datetime import timedelta

def get_data_by_user(time,user,type,xp,multiplier,xp_multiplied,level,channel, content):
    time = time - timedelta(hours=3)
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
    
    
    