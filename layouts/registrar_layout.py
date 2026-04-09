import PySimpleGUI as sg
import asyncio
from controllers.user_controller import UserController
from controllers.password_controller import PasswordController


class RegistrarLayout:
    def __init__(self):
        self.user_controller = UserController()
        self.layout = [
            [sg.Text("Registrar Novo Usuário")],
            [sg.Text("Usuário"), sg.Input(key="-USER-")],
            [sg.Text("Senha"), sg.Input(password_char="*", key="-PASS-")],
            [sg.Button("Registrar", key="-REGISTER-"), sg.Button("Sair", key="-EXIT-")],
        ]

    def get_layout(self):
        return self.layout

    def run(self):
        window = sg.Window("Registrar", self.layout)
        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, "-EXIT-"):
                break

            if event == "-REGISTER-":
                username = values.get("-USER-", "").strip()
                password = values.get("-PASS-", "")
                if not username or not password:
                    sg.popup("Preencha usuário e senha")
                    continue
                try:
                    success = asyncio.run(
                        self.user_controller.create_user(username, password)
                    )
                except Exception as e:
                    sg.popup(f"Erro no registro: {e}")
                    continue

                if success:
                    sg.popup("Usuário registrado com sucesso")
                    break
                else:
                    sg.popup("Falha ao registrar usuário")

        window.close()

if __name__ == "__main__":
    RegistrarLayout().run()