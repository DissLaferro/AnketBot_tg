import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_FILE = "ankety.json"

def load_database() -> Dict:
    """Загружает базу данных из файла"""
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"ankety": []}
    return {"ankety": []}

def save_database(data: Dict):
    """Сохраняет базу данных в файл"""
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_anketa(user_id: int, user_data: Dict, username: str = None):
    """Добавляет новую анкету в базу"""
    db = load_database()
    
    anketa = {
        "user_id": user_id,
        "username": username,
        "name": user_data.get('name'),
        "age": user_data.get('age'),
        "user_username": user_data.get('username'),
        "activity": user_data.get('activity'),
        "conflict": user_data.get('conflict'),
        "about": user_data.get('about'),
        "timezone": user_data.get('timezone'),
        "minecraft": user_data.get('minecraft'),
        "status": "pending",  # pending, accepted, rejected
        "created_at": datetime.now().isoformat()
    }
    
    db["ankety"].append(anketa)
    save_database(db)

def update_anketa_status(user_id: int, status: str):
    """Обновляет статус анкеты"""
    db = load_database()
    
    for anketa in db["ankety"]:
        if anketa["user_id"] == user_id and anketa["status"] == "pending":
            anketa["status"] = status
            anketa["updated_at"] = datetime.now().isoformat()
            break
    
    save_database(db)

def get_all_ankety(status: Optional[str] = None) -> List[Dict]:
    """Получает все анкеты, опционально фильтрует по статусу"""
    db = load_database()
    
    if status:
        return [a for a in db["ankety"] if a["status"] == status]
    
    return db["ankety"]

def get_anketa_by_user_id(user_id: int) -> Optional[Dict]:
    """Получает последнюю анкету пользователя"""
    db = load_database()
    
    for anketa in reversed(db["ankety"]):
        if anketa["user_id"] == user_id:
            return anketa
    
    return None
