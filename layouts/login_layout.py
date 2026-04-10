import PySimpleGUI as sg
import asyncio
from controllers.user_controller import UserController
from controllers.password_controller import PasswordController
from layouts.dashboard_layout import DashboardLayout


class LoginLayout:
    def __init__(self):
        self.user_controller = UserController()
        self.password_controller = PasswordController()

    def _clear_inputs(self, window, keys: list[str]):
        for k in keys:
            window[k].update("")

    def _tab_login(self):
        return sg.Tab(
            "Login",
            [
                [sg.Text("Usuário", font=("Helvetica", 10))],
                [sg.Input(key="-L-USER-", expand_x=True)],
                [sg.Text("Senha", font=("Helvetica", 10))],
                [sg.Input(password_char="•", key="-L-PASS-", expand_x=True)],
                [sg.VPush()],
                [sg.Button("Entrar", key="-LOGIN-", expand_x=True, size=(0, 1))],
                [sg.VPush()],
            ],
            key="-TAB-LOGIN-",
            pad=(16, 12),
        )

    def _tab_register(self):
        return sg.Tab(
            "Registrar",
            [
                [sg.Text("Usuário", font=("Helvetica", 10))],
                [sg.Input(key="-R-USER-", expand_x=True)],
                [sg.Text("Senha", font=("Helvetica", 10))],
                [sg.Input(password_char="•", key="-R-PASS-", expand_x=True)],
                [sg.VPush()],
                [
                    sg.Button(
                        "Criar conta", key="-REGISTER-", expand_x=True, size=(0, 1)
                    )
                ],
                [sg.VPush()],
            ],
            key="-TAB-REGISTER-",
            pad=(16, 12),
        )

    def _layout(self):
        return [
            [sg.VPush()],
            [
                sg.Push(),
                sg.Text(
                    "Gerenciador de Senhas",
                    font=("Helvetica", 14, "bold"),
                    justification="center",
                ),
                sg.Push(),
            ],
            [sg.HorizontalSeparator(pad=(0, 8))],
            [
                sg.TabGroup(
                    [[self._tab_login(), self._tab_register()]],
                    key="-TABGROUP-",
                    tab_location="top",
                    expand_x=True,
                    expand_y=True,
                )
            ],
            [sg.HorizontalSeparator(pad=(0, 4))],
            [sg.Push(), sg.Push()],
            [sg.VPush()],
        ]

    def run(self):
        sg.theme("Dark Brown") 

        window = sg.Window(
            "Gerenciador de Senhas",
            self._layout(),
            size=(400, 340),  
            finalize=True,
            element_padding=(4, 6),
        )

        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED:
                break

            if event == "-LOGIN-":
                username = values["-L-USER-"].strip()
                password = values["-L-PASS-"]

                if not username or not password:
                    sg.popup("Preencha usuário e senha.", title="Atenção")
                    continue

                try:
                    user_id = asyncio.run(self.user_controller.login(username, password))
                except Exception as e:
                    sg.popup(f"Erro no login: {e}", title="Erro")
                    continue

                if user_id:
                    self._clear_inputs(window, ["-L-USER-", "-L-PASS-"])
                    DashboardLayout(password_controller=self.password_controller, user_id=user_id).run()
                else:
                    sg.popup("Usuário ou senha inválidos.", title="Erro")

            if event == "-REGISTER-":
                username = values["-R-USER-"].strip()
                password = values["-R-PASS-"]

                if not username or not password:
                    sg.popup("Preencha usuário e senha.", title="Atenção")
                    continue

                try:
                    success = asyncio.run(self.user_controller.create_user(username, password))
                except Exception as e:
                    sg.popup(f"Erro no registro: {e}", title="Erro")
                    continue

                if success:
                    sg.popup("Conta criada! Faça login na aba ao lado.", title="Sucesso")
                    self._clear_inputs(window, ["-R-USER-", "-R-PASS-"])
                    window["-TABGROUP-"].Widget.select(0)
                else:
                    sg.popup("Falha ao registrar. Tente outro nome de usuário.", title="Erro")

        window.close()


if __name__ == "__main__":
    LoginLayout().run()
