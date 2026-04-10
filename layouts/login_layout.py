import PySimpleGUI as sg
import asyncio
from controllers.user_controller import UserController
from controllers.password_controller import PasswordController
from layouts.dashboard_layout import DashboardLayout


class LoginLayout:
    def __init__(self):
        self.user_controller = UserController()
        self.password_controller = PasswordController()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _clear_inputs(self, window, keys: list[str]):
        for k in keys:
            window[k].update("")

    def _tab_login(self):
        return sg.Tab(
            "Login",
            [
                [sg.VPush()],
                [sg.Text("Usuário"), sg.Input(key="-L-USER-", size=28)],
                [
                    sg.Text("Senha  "),
                    sg.Input(password_char="*", key="-L-PASS-", size=28),
                ],
                [sg.VPush()],
                [
                    sg.Push(),
                    sg.Button("Entrar", key="-LOGIN-", size=12),
                    sg.Push(),
                ],
                [sg.VPush()],
            ],
            key="-TAB-LOGIN-",
            pad=(10, 10),
        )

    def _tab_register(self):
        return sg.Tab(
            "Registrar",
            [
                [sg.VPush()],
                [sg.Text("Usuário"), sg.Input(key="-R-USER-", size=28)],
                [
                    sg.Text("Senha  "),
                    sg.Input(password_char="*", key="-R-PASS-", size=28),
                ],
                [sg.VPush()],
                [
                    sg.Push(),
                    sg.Button("Criar conta", key="-REGISTER-", size=12),
                    sg.Push(),
                ],
                [sg.VPush()],
            ],
            key="-TAB-REGISTER-",
            pad=(10, 10),
        )

    def _layout(self):
        return [
            [
                sg.Push(),
                sg.Text("🔐 Gerenciador de Senhas", font=("Helvetica", 16, "bold")),
                sg.Push(),
            ],
            [sg.HorizontalSeparator()],
            [
                sg.TabGroup(
                    [[self._tab_login(), self._tab_register()]],
                    key="-TABGROUP-",
                    tab_location="top",
                    expand_x=True,
                )
            ],
            [sg.HorizontalSeparator()],
            [sg.Push(), sg.Button("Sair", key="-EXIT-", size=8), sg.Push()],
        ]

    # ------------------------------------------------------------------
    # Event loop
    # ------------------------------------------------------------------

    def run(self):
        window = sg.Window(
            "Gerenciador de Senhas",
            self._layout(),
            size=(380, 280),
            finalize=True,
        )

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "-EXIT-"):
                break

            # ── LOGIN ──────────────────────────────────────────────────
            if event == "-LOGIN-":
                username = values["-L-USER-"].strip()
                password = values["-L-PASS-"]

                if not username or not password:
                    sg.popup("Preencha usuário e senha.", title="Atenção")
                    continue

                try:
                    user_id = asyncio.run(
                        self.user_controller.login(username, password)
                    )
                except Exception as e:
                    sg.popup(f"Erro no login: {e}", title="Erro")
                    continue

                if user_id:
                    self._clear_inputs(window, ["-L-USER-", "-L-PASS-"])
                    DashboardLayout(
                        password_controller=self.password_controller,
                        user_id=user_id,
                    ).run()
                else:
                    sg.popup("Usuário ou senha inválidos.", title="Erro")

            # ── REGISTRO ───────────────────────────────────────────────
            if event == "-REGISTER-":
                username = values["-R-USER-"].strip()
                password = values["-R-PASS-"]

                if not username or not password:
                    sg.popup("Preencha usuário e senha.", title="Atenção")
                    continue

                try:
                    success = asyncio.run(
                        self.user_controller.create_user(username, password)
                    )
                except Exception as e:
                    sg.popup(f"Erro no registro: {e}", title="Erro")
                    continue

                if success:
                    sg.popup(
                        "Conta criada! Faça login na aba ao lado.", title="Sucesso"
                    )
                    self._clear_inputs(window, ["-R-USER-", "-R-PASS-"])
                    window["-TABGROUP-"].Widget.select(0)  # volta para aba Login
                else:
                    sg.popup(
                        "Falha ao registrar. Tente outro nome de usuário.", title="Erro"
                    )

        window.close()


if __name__ == "__main__":
    LoginLayout().run()
