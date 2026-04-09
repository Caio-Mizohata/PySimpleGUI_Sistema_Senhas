import PySimpleGUI as sg
import asyncio
from layouts.new_password import NewPasswordLayout


class DashboardLayout:
    def __init__(self, passwords: dict, password_controller=None, user_id: int = None):
        # passwords: dict[site] = password (decrypted)
        self.passwords = passwords or {}
        self.password_controller = password_controller
        self.user_id = user_id
        self.revealed = set()

    def _build_table(self):
        def mask(pw: str) -> str:
            return "**********"

        table = []
        for site, pw in self.passwords.items():
            display = pw if site in self.revealed else mask(pw)
            table.append([site, display])
        return table

    def _reload_passwords(self):
        if not self.password_controller:
            return
        try:
            self.passwords = asyncio.run(
                self.password_controller.get_all_passwords(self.user_id)
            )
        except Exception:
            pass

    def run(self):
        layout = [
            [sg.Text("Dashboard")],
            [
                sg.Table(
                    values=self._build_table(),
                    headings=["Site", "Senha"],
                    key="-TABLE-",
                    auto_size_columns=True,
                    num_rows=10,
                    enable_events=True,
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                )
            ],
            [
                sg.Button("Revelar senha", key="-REVEAL-"),
                sg.Button("Adicionar", key="-ADD-"),
                sg.Button("Sair", key="-EXIT-"),
            ],
        ]

        window = sg.Window("Dashboard", layout)
        while True:
            event, values = window.read()
            if event in (sg.WIN_CLOSED, "-EXIT-"):
                break

            if event == "-REVEAL-":
                selected = values.get("-TABLE-", [])
                if not selected:
                    sg.popup("Selecione uma linha para revelar a senha")
                    continue
                row = selected[0]
                table = self._build_table()
                if row < 0 or row >= len(table):
                    continue
                site = table[row][0]
                if site in self.revealed:
                    self.revealed.remove(site)
                else:
                    self.revealed.add(site)
                window["-TABLE-"].update(values=self._build_table())

            if event == "-ADD-":
                # open new password dialog modally and then refresh table
                NewPasswordLayout(self.password_controller, self.user_id).run()
                self._reload_passwords()
                window["-TABLE-"].update(values=self._build_table())

        window.close()
        return None


if __name__ == "__main__":
    sample_passwords = {"Google": "senha123", "Facebook": "senha456"}
    DashboardLayout(sample_passwords).run()
