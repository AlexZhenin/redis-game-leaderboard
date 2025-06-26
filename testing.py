import time
import random
import threading
from datetime import datetime, timedelta
from models.player import create_player, update_player, delete_player
from models.level import add_level
from services.achievements import add_achievement, has_achievement, common_achievements
from services.leaderboard import add_score_to_leaderboard, get_top_players, get_player_rank_and_score
from services.activity import add_activity, get_recent_activities
from services.chat import subscribe_to_channel, publish_message
from models.cache import track_level_popularity, cache_popular_levels, get_level_data, get_player_data
from utils.redis_client import redis_client

if __name__ == "__main__":

    print("\n=== Тестирование CRUD-операций для профилей пользователей ===")
    create_player("test1", "test1", "test1@example.com")
    create_player("test2", "test2", "test2@example.com")
    print("Профиль test1:", get_player_data("test1"))
    print("Профиль test2:", get_player_data("test2"))
    # удаляем test1
    delete_player("test1")
    print("Профиль test1 после удаления:", get_player_data("test1"))


    print("\n=== Тестирование истечения времени для профилей пользователей ===")
    create_player("test3", "Player Three", "test3@example.com")
    redis_client.expire(f'user:test3', timedelta(seconds=10))# TTL = 10 секунд
    print("Профиль test3 создан:", get_player_data("test3"))
    time.sleep(12)  # Ждем, пока TTL истечет
    print("Профиль test3 после истечения TTL:", get_player_data("test3"))



    print("\n=== Тестирование чата и подписок ===")
    threading.Thread(target=subscribe_to_channel, args=('general',), daemon=True).start()
    threading.Thread(target=subscribe_to_channel, args=('achievements',), daemon=True).start()
    time.sleep(1)  # Даем подписчику время на подключение
    publish_message('general', "Привет всем!")
    time.sleep(1)  # Ждем, пока сообщение будет доставлено


    print("\n=== Тестирование достижений ===")
    add_achievement("test2", "First Win")
    add_achievement("test2", "Speed Runner")
    add_achievement("test3", "First Win")
    print("Есть ли у test2 достижение 'First Win'?:",
          "Да" if has_achievement("test2", "First Win") else "Нет")
    print("Есть ли у test2 достижение 'Speed Runner'?:",
          "Да" if has_achievement("test2", "Speed Runner") else "Нет")
    print("Есть ли у test3 достижение 'First Win'?:",
          "Да" if has_achievement("test3", "First Win") else "Нет")
    print("Есть ли у test3 достижение 'Speed Runner'?:",
          "Да" if has_achievement("test3", "Speed Runner") else "Нет")


    print("\n=== Поиск общих достижений ===")
    common = common_achievements("test2", "test3")
    print("Общие достижения test2 и test3:", common)


    print("\n=== Тестирование лидерборда ===")
    #add_score_to_leaderboard("test2", 1000)
    #add_score_to_leaderboard("test3", 800)
    #add_score_to_leaderboard("test4", 1200)
    print("Топ-10 игроков:", get_top_players())

    print("\n=== Ранг и счет игрока ===")
    rank, score = get_player_rank_and_score("test3")
    print(f"Ранг и счет test3: {rank} место, счет = {score}")

    print("\n=== Тестирование фида активности ===")
    add_activity("test2", "Прошел уровень 1")
    add_activity("test3", "Получил достижение First Win")
    print("Последние действия test2:", get_recent_activities("player2"))
    print("Последние действия test3:", get_recent_activities("player3"))
