import redis
import uuid

r = redis.Redis(host='localhost', port=6379, db=0)

def create_session(username:str, password:str) -> str:
    session_id = str(uuid.uuid4())
    r.set(session_id, username)
    r.expire(session_id, 300)
    return session_id

def get_session(session_id: str) -> str | None:
    value = r.get(session_id)
    if value:
        return value.decode("utf-8")
    return None

def get_all_session() -> list:
    session_keys = r.keys()
    sessions = [r.get(key).decode('utf-8') for key in session_keys]
    return sessions
    