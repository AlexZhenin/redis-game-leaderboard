import time
import random
import threading
from datetime import datetime
from models.player import create_player, update_player, delete_player
from models.level import add_level
from services.achievements import add_achievement, has_achievement, common_achievements
from services.leaderboard import add_score_to_leaderboard, get_top_players
from services.activity import add_activity, get_recent_activities
from services.chat import subscribe_to_channel, publish_message
from models.cache import track_level_popularity, cache_popular_levels, get_level_data, get_player_data

# Симуляция игры
def simulate_game():
    # Создаем 20 игроков
    players = [f"player{i}" for i in range(1, 21)]
    for player_id in players:
        create_player(player_id, f"Player {player_id}", f"{player_id}@example.com")

    # Создаем 20 уровней
    levels = [f"level{i}" for i in range(1, 21)]
    difficulties = ['Easy', 'Medium', 'Hard', 'Very Hard', 'Extreme']
    random_difficulty = random.choice(difficulties)
    for level_id in levels:
        add_level(level_id, f"Level {level_id}", random_difficulty)

    # Симуляция игрового процесса
    while True:
        # Выбираем случайного игрока
        player_id = random.choice(players)
        action = random.choice(['play_level', 'get_achievement', 'chat'])#, 'update_score'])
        player_data = get_player_data(player_id)
        if not player_data:
            print(f'Данные игрока {player_id} недоступны')
            continue

        if action == 'play_level':
            # Игрок проходит случайный уровень
            level_id = random.choice(levels)
            if not get_level_data(level_id):
                print(f'Данные уровня {level_id} недоступны')
                continue

            print(f"Игрок {player_id} проходит уровень {level_id}...")
            add_activity(player_id, f"Начал уровень {level_id}")
            time.sleep(random.randint(1, 3))  # Имитация времени прохождения уровня
            add_activity(player_id, f"Прошел уровень {level_id}")
            track_level_popularity(level_id)  # Увеличиваем популярность уровня
            print(f"Игрок {player_id} прошел уровень {level_id}!")

            # Игрок обновляет свой счет
            score = random.randint(100, 1000)
            add_score_to_leaderboard(player_id, score)
            print(f"Игрок {player_id} обновляет счет на {score} очков")
            add_activity(player_id, f"Обновил счет на {score} очков")

            add_score_to_leaderboard(player_id, score, level_id)
            add_activity(player_id, f"Обновил счет на {score} очков на уровне {level_id}")

            current_level = player_data.get('level')
            update_player(player_id, 'level', int(current_level)+1)
            add_activity(player_id, f"Повысил уровень! Теперь игрок имеет {int(current_level)+1} уровень!")
            publish_message('general', f'{player_id} повысил уровень до {int(current_level)+1}!')

        elif action == 'get_achievement':
            # Игрок получает случайное достижение
            achievements = ['First Win', 'Speed Runner', 'Explorer', 'Boss Slayer']
            achievement = random.choice(achievements)
            if not has_achievement(player_id, achievement):
                add_achievement(player_id, achievement)
                print(f"Игрок {player_id} получил достижение: {achievement}")
                add_activity(player_id, f"Получил достижение: {achievement}")
            else:
                print(f"Игрок {player_id} уже имеет достижение: {achievement}")

        elif action == 'chat':
            # Игрок пишет в чат
            messages = [
                "Привет всем!",
                "Как дела?",
                "Кто тут?",
                "Давайте играть!",
                "Я новичок, помогите!"
            ]
            message = random.choice(messages)
            print(f"Игрок {player_id} пишет в чат: {message}")
            publish_message('general', f"{player_id}: {message}")
            add_activity(player_id, f"Написал в чат: {message}")

        # Пауза между действиями
        time.sleep(random.randint(1, 3))

# Функция для планировщика обновления кэша популярных уровней
def schedule_cache_update():
    """
    Планировщик для обновления кэша популярных уровней.
    """
    while True:
        print("Обновление кэша для популярных уровней...")
        cache_popular_levels()
        time.sleep(60)  # Обновление каждую минуту

# Основная функция
if __name__ == "__main__":
    # Подписчик чата
    threading.Thread(target=subscribe_to_channel, args=('general',), daemon=True).start()
    threading.Thread(target=subscribe_to_channel, args=('achievements',), daemon=True).start()
    threading.Thread(target=subscribe_to_channel, args=('cache',), daemon=True).start()

    # Вывод топ-10 игроков каждые 10 секунд
    def print_leaderboard():
        while True:
            print("\n--- Топ-10 игроков ---")
            top_players = get_top_players()
            for rank, (player_id, score) in enumerate(top_players, start=1):
                print(f"{rank}. {player_id}: {score} очков")
            print("----------------------\n")
            time.sleep(10)

    # Вывод последних активностей каждые 15 секунд
    def print_recent_activities():
        while True:
            print("\n--- Последние активности ---")
            for player_id in [f"player{i}" for i in range(1, 21)]:
                activities = get_recent_activities(player_id, count=3)
                if activities:
                    print(f"{player_id}: {', '.join(activities)}")
            print("----------------------------\n")
            time.sleep(15)

    # Запуск лидерборда и активности в отдельных потоках
    #threading.Thread(target=print_leaderboard, daemon=True).start()
    #threading.Thread(target=print_recent_activities, daemon=True).start()

    # Запуск планировщика для обновления кэша популярных уровней
    threading.Thread(target=schedule_cache_update, daemon=True).start()

    # Запуск симуляции игры
    simulate_game()
