import os
import sys
import asyncio
from config.database import init_db
from layouts.login_layout import LoginLayout

# Garante que a pasta atual esteja no path para imports locais
sys.path.append(os.path.dirname(__file__))


def main():
    try:
        asyncio.run(init_db())
    except Exception as e:
        print(f"Falha ao inicializar DB: {e}")

    try:
        LoginLayout().run()
    except KeyboardInterrupt:
        print("Encerrando aplicação...")


if __name__ == "__main__":
    main()
