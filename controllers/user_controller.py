import asyncio
import sqlite3
from config.database import pre_save_password, verify_password


class UserController:
    def __init__(self, db_path: str = "banco_dados.db"):
        self.db_path = db_path

    async def create_user(self, username: str, password: str) -> bool:
        conn = None
        try:
            hashed_password = await asyncio.to_thread(pre_save_password, password)
            conn = sqlite3.connect(self.db_path)
            conn.execute("INSERT INTO users (username, passwordHash) VALUES (?, ?)",(username, hashed_password),)
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao criar usuário: {e}")
            return False
        finally:
            if conn:
                conn.close()

    async def login(self, username: str, password: str) -> int | None:
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            row = conn.execute("SELECT id, passwordHash FROM users WHERE username = ?", (username,)).fetchone()
            if row:
                user_id, stored_hash = row
                ok = await asyncio.to_thread(verify_password, stored_hash, password)
                if ok:
                    return user_id
            return None
        except Exception as e:
            print(f"Erro ao realizar login: {e}")
            return None
        finally:
            if conn:
                conn.close()
