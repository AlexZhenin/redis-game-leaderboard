import redis
import json
from datetime import datetime, timedelta

# Подключение к Redis
redis_client = redis.Redis(host='localhost', port=6379)

# 1) Кэш профилей пользователя
def create_user_profile(user_id, profile_data):
    """Создание профиля пользователя."""
    for field, value in profile_data.items():
        redis_client.hset(f'user:{user_id}', field, value)
    redis_client.expire(f'user:{user_id}', 3600)  # Установка времени истечения


def get_user_profile(user_id):
    """Получение профиля пользователя."""
    return redis_client.hgetall(f'user:{user_id}')

def update_user_profile(user_id, profile_data):
    """Обновление профиля пользователя."""
    for field, value in profile_data.items():
        redis_client.hset(f'user:{user_id}', field, value)

def delete_user_profile(user_id):
    """Удаление профиля пользователя."""
    redis_client.delete(f'user:{user_id}')

# 2) Трекинг достижений
def add_achievement(user_id, achievement):
    """Добавление достижения пользователю."""
    redis_client.sadd(f'user:{user_id}:achievements', achievement)

def has_achievement(user_id, achievement):
    """Проверка наличия достижения у пользователя."""
    return redis_client.sismember(f'user:{user_id}:achievements', achievement)

def get_common_achievements(user_id1, user_id2):
    """Получение общих достижений между двумя пользователями."""
    return redis_client.sinter(f'user:{user_id1}:achievements', f'user:{user_id2}:achievements')

# 3) Игровой лидерборд
def add_score_to_leaderboard(user_id, score, game_level='global'):
    """Добавление баллов для пользователя в лидерборд."""
    redis_client.zadd(f'leaderboard:{game_level}', {user_id: score})

def get_top_players(game_level='global', count=10):
    """Получение топ-игроков."""
    return redis_client.zrevrange(f'leaderboard:{game_level}', 0, count - 1, withscores=True)

def get_player_rank_and_score(user_id, game_level='global'):
    """Получение ранга и счета конкретного игрока."""
    rank = redis_client.zrevrank(f'leaderboard:{game_level}', user_id)
    score = redis_client.zscore(f'leaderboard:{game_level}', user_id)
    return rank, score

# 4) Feed недавних событий
def add_activity(user_id, activity):
    """Добавление нового события в feed."""
    activity_data = {'timestamp': datetime.now().isoformat(), 'activity': activity}
    redis_client.lpush(f'user:{user_id}:activity', json.dumps(activity_data))
    redis_client.ltrim(f'user:{user_id}:activity', 0, 99)  # Обрезка до последних 100 элементов

def get_recent_activities(user_id, count=10):
    """Получение последних событий из feed."""
    activities = redis_client.lrange(f'user:{user_id}:activity', 0, count - 1)
    return [json.loads(activity) for activity in activities]



# Примеры использования
if __name__ == "__main__":
    # Создание профиля пользователя
    create_user_profile('user1', {'name': 'Alice', 'email': 'alice@example.com'})

    # Получение профиля пользователя
    print(get_user_profile('user1'))

    # Добавление достижения
    add_achievement('user1', 'First Win')

    # Проверка наличия достижения
    print(has_achievement('user1', 'First Win'))

    # Добавление баллов в лидерборд
    add_score_to_leaderboard('user1', 1000)

    # Получение топ-игроков
    print(get_top_players())

    # Добавление события в feed
    add_activity('user1', 'Completed level 1')

    # Получение последних событий
    print(get_recent_activities('user1'))



