import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

# Создание клиента Redis
def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

redis_client = get_redis_client()
