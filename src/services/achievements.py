from utils.redis_client import redis_client

def add_achievement(player_id, achievement):
    """
    Добавление достижения для игрока.
    """
    redis_client.sadd(f'achievements:{player_id}', achievement)
    redis_client.publish('achievements', f"Игрок {player_id} получил достижение: {achievement}")
    #print(f"Достижение '{achievement}' добавлено для игрока {player_id}.")

def has_achievement(player_id, achievement):
    """
    Проверка наличия достижения у игрока.
    """
    return redis_client.sismember(f'achievements:{player_id}', achievement)

def common_achievements(player1_id, player2_id):
    """
    Поиск общих достижений между двумя игроками.
    """
    return redis_client.sinter(f'achievements:{player1_id}', f'achievements:{player2_id}')
