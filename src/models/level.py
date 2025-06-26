import json
from datetime import datetime, timedelta
from utils.redis_client import redis_client

def add_level(level_id, name, difficulty='Medium', description=''):
    """Добавление уровня."""
    level_data = {
        'level_id': level_id,
        'name': name,
        'difficulty': difficulty,
        'description': description,
        'created_at': datetime.now().isoformat()
    }
    with redis_client.pipeline() as pipe:
        pipe.multi()
        pipe.set(f'level:{level_id}', json.dumps(level_data))
        pipe.expire(f'level:{level_id}', timedelta(minutes=60))  # Устанавливаем TTL 60 минут
        pipe.execute()
    print(f"Уровень {level_id} добавлен.")

'''
def get_level(level_id):
    """Получение данных уровня."""
    level_data = redis_client.get(f'level:{level_id}')
    if level_data:
        return json.loads(level_data)
    return None
'''