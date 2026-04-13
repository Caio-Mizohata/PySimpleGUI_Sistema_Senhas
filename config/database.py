from argon2 import PasswordHasher
import sqlite3
import datetime

horario_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def init_db() -> None:
    try:
        conn = sqlite3.connect("banco_dados.db")
        cursor = conn.cursor()

        # criar tabelas se não existirem
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                passwordHash TEXT NOT NULL
            )
            """
        )
        
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                servico TEXT NOT NULL,
                credencial TEXT NOT NULL,
                password TEXT NOT NULL,
                notes TEXT DEFAULT NULL,
                user_id INTEGER,
                created_at TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
                updated_at TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )

         # Trigger para atualizar o campo created_at na tabela passwords
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS save_passwords_created_at
            AFTER INSERT ON passwords
            FOR EACH ROW
            BEGIN
               UPDATE passwords
               SET created_at = datetime('now','localtime')
               WHERE id = NEW.id;
            END;
            """
        )

        # Trigger para atualizar o campo updated_at na tabela passwords
        cursor.execute(
            """
            CREATE TRIGGER IF NOT EXISTS update_passwords_updated_at
            AFTER UPDATE ON passwords
            FOR EACH ROW
            BEGIN
               UPDATE passwords
               SET updated_at = datetime('now','localtime')
               WHERE id = OLD.id;
            END;
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
        time_cost=3, 
        memory_cost=64 * 1024, # 64 MB
        parallelism=2, 
        hash_len=32, 
        salt_len=16
    )
    return password_hasher.hash(password)


def verify_password(stored_hash: str, provided_password: str) -> bool:
    password_hasher = PasswordHasher(
        time_cost=3, 
        memory_cost=64 * 1024, # 64 MB
        parallelism=2, 
        hash_len=32, 
        salt_len=16
    )

    try:
        password_hasher.verify(stored_hash, provided_password)
        return True
    except Exception as e:
        print(f"Erro ao verificar senha: {e}")
        return False
