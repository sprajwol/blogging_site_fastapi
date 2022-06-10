from redis import Redis
# Setup our redis connection for storing the denylist tokens
redis_conn = Redis(host='localhost', port=6379, db=0, decode_responses=True)
