import time

queries = 0


def fetch_user(user_id):
    global queries
    queries += 1
    time.sleep(2)
    return {"id": user_id, "name": "Asha", "role": "Developer"}
