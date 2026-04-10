import asyncio
import sqlite3
from services.encrypt_service import EncryptService
import os
from dotenv import load_dotenv


class PasswordController:
    def __init__(self, db_path: str = "banco_dados.db"):
        self.db_path = db_path
        load_dotenv()
        self.encrypt_service = EncryptService(key=bytes.fromhex(os.getenv("AES_KEY")))

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    async def save_password(self, servico: str, credencial: str, password: str, notes: str, user_id: int) -> bool:
        conn = None
        try:
            encrypted_password = await asyncio.to_thread(self.encrypt_service.encrypt, password)
            conn = self._connect()
            conn.execute(
                "INSERT INTO passwords (user_id, servico, credencial, password, notes) VALUES (?, ?, ?, ?, ?)",
                (user_id, servico, credencial, encrypted_password, notes),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar senha: {e}")
            return False
        finally:
            if conn:
                conn.close()

    async def get_password(self, servico: str, user_id: int) -> str | None:
        conn = None
        try:
            conn = self._connect()
            row = conn.execute("SELECT password FROM passwords WHERE servico = ? AND user_id = ?",(servico, user_id),).fetchone()
            if row:
                return await asyncio.to_thread(self.encrypt_service.decrypt, row[0])
            return None
        except Exception as e:
            print(f"Erro ao recuperar senha: {e}")
            return None
        finally:
            if conn:
                conn.close()

    async def get_all_passwords(self, user_id: int) -> dict:
        conn = None
        try:
            conn = self._connect()
            rows = conn.execute(
                "SELECT servico, credencial, password, notes FROM passwords WHERE user_id = ?",(user_id,),).fetchall()
            result = {}
            for servico, credencial, encrypted_password, notes in rows:
                try:
                    dec = await asyncio.to_thread(self.encrypt_service.decrypt, encrypted_password)
                except Exception:
                    dec = "<erro>"
                result[servico] = {
                    "credencial": credencial or "",
                    "password": dec,
                    "notes": notes or "",
                }
            return result
        except Exception as e:
            print(f"Erro ao listar senhas: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    async def update_password(self, servico: str, credencial: str, password: str, notes: str, user_id: int) -> bool:
        conn = None
        try:
            encrypted_password = await asyncio.to_thread(self.encrypt_service.encrypt, password)
            conn = self._connect()
            conn.execute(
                "UPDATE passwords SET credencial = ?, password = ?, notes = ? WHERE servico = ? AND user_id = ?",
                (credencial, encrypted_password, notes, servico, user_id),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar senha: {e}")
            return False
        finally:
            if conn:
                conn.close()

    async def delete_password(self, servico: str, user_id: int) -> bool:
        conn = None
        try:
            conn = self._connect()
            conn.execute(
                "DELETE FROM passwords WHERE servico = ? AND user_id = ?",
                (servico, user_id),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao deletar senha: {e}")
            return False
        finally:
            if conn:
                conn.close()
                