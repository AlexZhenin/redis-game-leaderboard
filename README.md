## Пояснения к коду
- Создается несколько потоков для просмотра (подписки на ) каналы (general, achievement, cache) и для обновления кэша популярных уровней.
    - В general выводятся сообщения в чате от игроков и некоторые активности.
    - В achievement выводятся сообщения о получении достижений игроками.
    - В cache выводятся сообщения об обновлении кэша популярных уровней.
- В коде есть вывод лидерборда и активностей раз в некоторое время (вывод только в консоль для наглядности)
- Создается 20 игроков, 20 уровней.

### Симуляция
- Симуляция запускается из "main.py".
- Симулируется активность случайного игрока: проходит случайно выбранный уровень, получает достижение или пишет в чат
    - При прохождении уровня, уровень становится более популярным (на 1); игрок обновляет свой счет в общем лидерборде и в лидерборде этого уровня; также игрок повышает свой уровень на 1.
    - Активности публикуются в соответствующие каналы.

### Проверка кэша и запрос к "БД"
- При получении данных пользователя сначала проверяется редис (кэш). Если данных нет, то имитируется запрос в БД. Примерно то же и для уровня.
def fetch_player_data_from_db(player_id):
    time.sleep(2)  """Имитируем задержку"""

    """Генерация случайной даты в диапазоне от 2023-01-01 до 2024-12-31"""
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    random_days = random.randint(0, (end_date - start_date).days)
    random_date = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

    return {
        'name': f'Player {player_id}',
        'email': f'{player_id}@example.com',
        'level': 1,
        'created_at': random_date
    }

def get_player_data(player_id):
    """Получение данных пользователя с кэшированием."""
    cached_data = redis_client.hgetall(f'user:{player_id}')
    if cached_data:
        print(f"Данные пользователя {player_id} найдены в кэше")
        #print(cached_data)
        #return json.loads(cached_data)
        return cached_data

    print(f"Загрузка данных пользователя {player_id} из базы данных...")
    player_data = fetch_player_data_from_db(player_id)

    with redis_client.pipeline() as pipe:
        pipe.multi()
        for field, value in player_data.items():
            pipe.hset(f'user:{player_id}', field, value)
        pipe.expire(f'user:{player_id}', timedelta(minutes=60))  # Устанавливаем TTL 60 минут
        pipe.execute()
    print(f"Данные пользователя {player_id} закэшированы")
    return player_data

### Код игрока
- Игрок создается через hset с TTL 60 минут. При какой-либо активности таймер обновляется до 60 минут.
def create_player(player_id, name, email):
    """
    Создание профиля игрока.
    """
    player_data = {
        'name': name,
        'email': email,
        'level': 1,
        'created_at': datetime.now().isoformat()
    }
    with redis_client.pipeline() as pipe:
        pipe.multi()
        for field, value in player_data.items():
            pipe.hset(f'user:{player_id}', field, value)
        pipe.expire(f'user:{player_id}', timedelta(minutes=60))  # Устанавливаем TTL 60 минут
        pipe.execute()
    print(f"Игрок {player_id} создан.")

### Код уровня и его обновления
#### Код уровня
- Создается через set и json.dumps с TTL 60 минут.
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

#### Обновление
- Если уровень становится популярным (входит в топ-10 популярных уровней), то запускается данная функция и его TTL обновляется до 2 часов.
def update_level_cache(level_id, level_data):
    """
    Атомарно обновляет кэш данных уровня.
    """
    with redis_client.pipeline() as pipe:
        pipe.multi()
        pipe.setex(f'level:{level_id}', 7200, json.dumps(level_data))
        pipe.execute()
    #print(f"Кэш уровня {level_id} обновлен атомарно")
    redis_client.publish('cache', f"Обновление кэша для популярного уровня {level_id}")


### Тесты
- В testing.py попунктные тесты возможностей (CRUD, TTL, чат и подписки, достижения и т.п.)
