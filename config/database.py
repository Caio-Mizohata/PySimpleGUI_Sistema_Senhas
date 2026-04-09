from argon2 import PasswordHasher
import sqlite3
import os


async def init_db() -> None:
    try:
        conn = sqlite3.connect("banco_dados.db")
        cursor = conn.cursor()
        # criar tabelas se não existirem
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servico TEXT NOT NULL,
                email TEXT,
                password TEXT NOT NULL,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                passwordHash TEXT NOT NULL
            )
            """
        )
        conn.commit()
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
    finally:
        if conn:
            conn.close()


def pre_save_password(password: str) -> str:
    password_hasher = PasswordHasher(
        time_cost=3, memory_cost=64 * 1024, parallelism=2, hash_len=32, salt_len=16
    )
    return password_hasher.hash(password)


def verify_password(stored_hash: str, provided_password: str) -> bool:
    password_hasher = PasswordHasher(
        time_cost=3, memory_cost=64 * 1024, parallelism=2, hash_len=32, salt_len=16
    )
    try:
        password_hasher.verify(stored_hash, provided_password)
        return True
    except Exception as e:
        print(f"Erro ao verificar senha: {e}")
        return False
