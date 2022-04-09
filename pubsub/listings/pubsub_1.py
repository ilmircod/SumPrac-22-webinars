import redis

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0


def main():
    bob_r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    bob_p = bob_r.pubsub()
    bob_p.subscribe('classical_music')

    alice_r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    alice_r.publish('classical_music', 'Alice Music')

    bob_p.get_message()
    new_music = bob_p.get_message()['data']
    print(new_music)

    alice_r.publish('classical_music', 'Alice 2nd Music')
    another_music = bob_p.get_message()['data']
    print(another_music)


if __name__ == "__main__":
    main()

# TODO: сделать с колбэком
