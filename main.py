import os
import sys
import threading
import asyncio
from config.database import init_db
from layouts.login_layout import LoginLayout

# garantir que a pasta atual esteja no path para imports locais
sys.path.append(os.path.dirname(__file__))


def start_gui():
    LoginLayout().run()


def main():
    try:
        asyncio.run(init_db())
    except Exception as e:
        print(f"Falha ao inicializar DB: {e}")

    # roda a interface gráfica em uma thread separada
    gui_thread = threading.Thread(target=start_gui, daemon=False)
    gui_thread.start()

    try:
        while gui_thread.is_alive():
            gui_thread.join(0.5)
    except KeyboardInterrupt:
        print("Encerrando aplicação...")


if __name__ == "__main__":
    main()
