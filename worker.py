import os
from dotenv import load_dotenv
import redis
from rq import Worker, Queue, Connection


load_dotenv()

listen = ['default']
ssl_cert_conn = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
)

# ssl_cert_conn.ping()

if __name__ == '__main__':
    with Connection(ssl_cert_conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
