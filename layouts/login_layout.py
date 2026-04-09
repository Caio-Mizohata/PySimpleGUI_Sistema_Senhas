import PySimpleGUI as sg
import asyncio
from controllers.user_controller import UserController
from controllers.password_controller import PasswordController
from layouts.registrar_layout import RegistrarLayout
from layouts.dashboard_layout import DashboardLayout
from layouts.new_password import NewPasswordLayout


class LoginLayout:
    def __init__(self):
        self.user_controller = UserController()
        self.password_controller = PasswordController()
        self.layout = [
            [sg.Text("Login")],
            [sg.Text("Usuário"), sg.Input(key="-USER-")],
            [sg.Text("Senha"), sg.Input(password_char="*", key="-PASS-")],
            [
                sg.Button("Entrar", key="-LOGIN-"),
                sg.Button("Registrar", key="-REGISTER-"),
                sg.Button("Sair", key="-EXIT-"),
            ],
        ]

    def get_layout(self):
        return self.layout

    def run(self):
        window = sg.Window("Login", self.layout)
        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, "-EXIT-"):
                break

            if event == "-REGISTER-":
                RegistrarLayout().run()

            if event == "-LOGIN-":
                username = values.get("-USER-", "").strip()
                password = values.get("-PASS-", "")
                if not username or not password:
                    sg.popup("Preencha usuário e senha")
                    continue
                try:
                    user_id = asyncio.run(
                        self.user_controller.login(username, password)
                    )
                except Exception as e:
                    sg.popup(f"Erro no login: {e}")
                    continue

                if user_id:
                    passwords = asyncio.run(
                        self.password_controller.get_all_passwords(user_id)
                    )
                    DashboardLayout(
                        passwords, password_controller=self.password_controller, user_id=user_id
                    ).run()
                else:
                    sg.popup("Usuário ou senha inválidos")

        window.close()


if __name__ == "__main__":
    LoginLayout().run()
