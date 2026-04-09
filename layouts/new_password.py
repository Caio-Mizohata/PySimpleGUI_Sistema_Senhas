import PySimpleGUI as sg
import asyncio
from controllers.password_controller import PasswordController


class NewPasswordLayout:
    def __init__(self, password_controller: PasswordController, user_id: int):
        self.password_controller = password_controller
        self.user_id = user_id
        self.layout = [
            [sg.Text("Registrar Nova Senha")],
            [sg.Text("Site"), sg.Input(key="-SITE-")],
            [sg.Text("Senha"), sg.Input(password_char="*", key="-PASS-")],
            [sg.Button("Salvar", key="-SAVE-"), sg.Button("Sair", key="-EXIT-")],
        ]

    def get_layout(self):
        return self.layout

    def run(self):
        window = sg.Window("Registrar Senha", self.layout)
        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, "-EXIT-"):
                break

            if event == "-SAVE-":
                site = values.get("-SITE-", "").strip()
                passwd = values.get("-PASS-", "")
                if not site or not passwd:
                    sg.popup("Preencha site e senha")
                    continue
                try:
                    ok = asyncio.run(
                        self.password_controller.save_password(site, "", passwd, self.user_id)
                    )
                except Exception as e:
                    sg.popup(f"Erro ao salvar: {e}")
                    continue
                if ok:
                    sg.popup("Senha salva com sucesso")
                    break
                else:
                    sg.popup("Falha ao salvar senha")

        window.close()


if __name__ == "__main__":
    # preview with dummy controller and user_id=1
    pc = PasswordController()
    NewPasswordLayout(pc, 1).run()
