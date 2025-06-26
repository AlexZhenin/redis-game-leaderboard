import redis

# 1) Подключение
redis_client = redis.Redis(host='localhost', port=6379)

if __name__ == "__main__":
    # 2.а) Установка и получение строки
    redis_client.set("test_str", "Hello World")
    print("String value:", redis_client.get("test_str").decode())

    # 2.б) TTL
    redis_client.setex("temp_key", 30, "Expiring soon")
    print("TTL:", redis_client.ttl("temp_key"), "sec")

    # 2.в) Счетчик
    redis_client.set("counter", 10)
    redis_client.incr("counter")
    redis_client.decrby("counter", 2)
    print("Counter:", redis_client.get("counter"))

    # 2.г) Проверка и удаление
    print("Exists before delete:", redis_client.exists("test_str"))
    redis_client.delete("test_str")
    print("Exists after delete:", redis_client.exists("test_str"))

    # 3) Pipeline
    pipe = redis_client.pipeline()
    pipe.set("p_key1", "pipe_value")
    pipe.incr("p_counter")
    pipe.get("p_key1")
    pipe_results = pipe.execute()
    print("Pipeline results:", pipe_results)