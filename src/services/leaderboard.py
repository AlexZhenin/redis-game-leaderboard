from utils.redis_client import redis_client

def add_score_to_leaderboard(user_id, score, game_level='global'):
    """
    Добавление баллов для пользователя в лидерборд.
    """
    redis_client.zadd(f'leaderboard:{game_level}', {user_id: score})
    print(f"Счет пользователя {user_id} обновлен на {score} очков")

'''
def update_level_leaderboard(level_id, player_id, score):
    """
    Обновляет лидерборд для конкретного уровня.
    """
    redis_client.zadd(f'level_leaderboard:{level_id}', {player_id: score})
    print(f"Лидерборд уровня {level_id} обновлен: игрок {player_id} набрал {score} очков.")
'''

def get_top_players(game_level='global', count=10):
    """
    Получение топ-игроков.
    """
    return redis_client.zrevrange(f'leaderboard:{game_level}', 0, count - 1, withscores=True)

def get_player_rank_and_score(user_id, game_level='global'):
    """
    Получение ранга и счета конкретного игрока.
    """
    rank = redis_client.zrevrank(f'leaderboard:{game_level}', user_id)
    score = redis_client.zscore(f'leaderboard:{game_level}', user_id)
    return rank, score
