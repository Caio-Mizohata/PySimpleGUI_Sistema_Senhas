import sqlite3
from config.database import pre_save_password, verify_password
import asyncio

class UserController:
    def __init__(self, db_path="banco_dados.db"):
        self.db_path = db_path

    async def create_user(self, username: str, password: str) -> bool:
        try:
            hashed_password = await asyncio.get_event_loop().run_in_executor(None, pre_save_password, password)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, passwordHash) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return False
        finally:
            if conn:
                conn.close()

    async def login(self, username: str, password: str):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, passwordHash FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
                stored_hash = result[1]
                ok = await asyncio.get_event_loop().run_in_executor(None, verify_password, stored_hash, password)
                if ok:
                    return user_id
            return None
        except Exception as e:
            print(f"Erro ao realizar login: {e}")
            return None
        finally:
            if conn:
                conn.close()
    