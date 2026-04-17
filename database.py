import json
import os

DB_FILE = "data.json"


# ========= 初始化 =========

def _load():
    if not os.path.exists(DB_FILE):
        return {
            "users": {},
            "history": []
        }

    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ========= 訂閱系統 =========

def subscribe(user_id, target):
    data = _load()

    user_id = str(user_id)

    if user_id not in data["users"]:
        data["users"][user_id] = []

    if target not in data["users"][user_id]:
        data["users"][user_id].append(target)

    _save(data)


def unsubscribe(user_id, target):
    data = _load()

    user_id = str(user_id)

    if user_id in data["users"]:
        if target in data["users"][user_id]:
            data["users"][user_id].remove(target)

    _save(data)


def get_user_targets(user_id):
    data = _load()
    return data["users"].get(str(user_id), [])


def get_users():
    data = _load()
    return list(data["users"].keys())


# ========= 去重系統 =========

def is_new(item):
    data = _load()

    if item in data["history"]:
        return False

    return True


def save_history(item):
    data = _load()

    if item not in data["history"]:
        data["history"].append(item)

        # 防止無限增長（保留最新500筆）
        data["history"] = data["history"][-500:]

    _save(data)
