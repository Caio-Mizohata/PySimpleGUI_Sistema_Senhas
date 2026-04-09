import sqlite3
from services.encrypt_service import EncryptService


class PasswordController:
    def __init__(self, db_path="banco_dados.db"):
        self.db_path = db_path
        self.encrypt_service = EncryptService(
            key=b"16-byte-long-key-for-AES"
        )  # Replace with your actual key

    async def save_password(
        self, servico: str, email: str, password: str, user_id: int
    ) -> bool:
        try:
            encrypted_password = self.encrypt_service.encrypt(password)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO passwords (user_id, servico, email, password) VALUES (?, ?, ?, ?)",
                (user_id, servico, email, encrypted_password),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao salvar senha: {e}")
            return False
        finally:
            if conn:
                conn.close()

    async def get_password(self, servico: str, user_id: int) -> str:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password FROM passwords WHERE servico = ? AND user_id = ?",
                (servico, user_id),
            )
            result = cursor.fetchone()
            if result:
                return self.encrypt_service.decrypt(
                    result[0]
                )  # Retorna a senha descriptografada
            return None
        except Exception as e:
            print(f"Erro ao recuperar senha: {e}")
            return None
        finally:
            if conn:
                conn.close()

    async def update_password(
        self, servico: str, email: str, password: str, user_id: int
    ) -> bool:
        try:
            encrypted_password = self.encrypt_service.encrypt(password)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE passwords SET email = ?, password = ? WHERE servico = ? AND user_id = ?",
                (email, encrypted_password, servico, user_id),
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar senha: {e}")
            return False
        finally:
            if conn:
                conn.close()

    async def get_all_passwords(self, user_id: int) -> dict:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT servico, password FROM passwords WHERE user_id = ?", (user_id,)
            )
            rows = cursor.fetchall()
            result = {}
            for servico, enc in rows:
                try:
                    dec = self.encrypt_service.decrypt(enc)
                except Exception:
                    dec = "<erro>"
                result[servico] = dec
            return result
        except Exception as e:
            print(f"Erro ao listar senhas: {e}")
            return {}
        finally:
            if conn:
                conn.close()
