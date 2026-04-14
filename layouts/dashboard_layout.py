import asyncio
import PySimpleGUI as sg
from controllers.password_controller import PasswordController
from layouts.update_layout import UpdateLayout
from helpers.dashboard_helper import DashboardHelper


class DashboardLayout:
    def __init__(self, password_controller: PasswordController = None, user_id: int = None):
        self.password_controller = password_controller
        self.user_id = user_id
        self.helper = DashboardHelper(self.password_controller, self.user_id)
        self.revealed = self.helper.revealed
        

    # Layout builders
    def _table_panel(self) -> list:
        return [
            [
                sg.Table(
                    values=self.helper._build_table(),
                    headings=["Serviço", "Credencial", "Senha", "Notas"],
                    key="-TABLE-",
                    auto_size_columns=False,
                    col_widths=[18, 20, 16, 24],
                    num_rows=13,
                    enable_events=True,
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    expand_x=True,
                    expand_y=True,
                    justification="left",
                    alternating_row_color=sg.theme_background_color(),
                )
            ],
            [sg.HorizontalSeparator(pad=(0, (8, 4)))],
            [
                sg.Button("Revelar / Ocultar", key="-REVEAL-", size=(20, 1)),
                sg.Push(),
                sg.Button("Editar", key="-EDIT-", size=(12, 1)),
                sg.Button("Remover", key="-DELETE-", size=(12, 1), button_color=("white", "#c0392b")),
            ],
        ]

    def _form_panel(self) -> list:
        label_size = (9, 1)
        input_size = 24

        return [
            [sg.Text("Nova Senha", font=("Helvetica", 11, "bold"), pad=(0, (0, 2)))],
            [sg.HorizontalSeparator(pad=(0, (0, 8)))],
            [
                sg.Text("Serviço", size=label_size),
                sg.Input(key="-SERVICO-", size=input_size, tooltip="Ex: Gmail, GitHub…"),
            ],
            [
                sg.Text("Credencial", size=label_size),
                sg.Input(key="-CREDENCIAL-", size=input_size, tooltip="Usuário ou e-mail"),
            ],
            [
                sg.Text("Senha", size=label_size),
                sg.Input(password_char="*", key="-PASS-", size=input_size),
            ],
            [
                sg.Text("Notas", size=label_size),
                sg.Multiline(key="-NOTES-", size=(input_size, 3), no_scrollbar=True),
            ],
            [sg.HorizontalSeparator(pad=(0, (8, 8)))],
            [sg.Push(), sg.Button("💾  Salvar", key="-SAVE-", size=(14, 1)), sg.Push()],
        ]

    def _layout(self) -> list:
        # Cabeçalho, tabela e formulário lado a lado
        return [
            [
                sg.Text("Painel principal", font=("Helvetica", 14, "bold")),
                sg.Push(),
                sg.Button("Sair", key="-EXIT-", size=(8, 1)),
            ],
            [sg.HorizontalSeparator(pad=(0, (2, 8)))], 
            [
                sg.Column(
                    self._table_panel(),
                    expand_x=True,
                    expand_y=True,
                    vertical_alignment="top",
                    pad=(0, 0),
                ),
                sg.VerticalSeparator(pad=(10, 0)),
                sg.Column(
                    self._form_panel(),
                    size=(270, None),
                    vertical_alignment="top",
                    pad=(8, 0),
                ),
            ],
        ]

   
    # Event loop
    def run(self):
        self.helper._reload_passwords()

        window = sg.Window(
            "Gerenciador de Senhas",
            self._layout(),
            size=(1056, 580),
            resizable=True,
            finalize=True,
        )

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "-EXIT-"):
                break

            selected = values.get("-TABLE-", [])
            table = self.helper._build_table()
            row_idx = selected[0] if selected else -1
            servico = table[row_idx][0] if 0 <= row_idx < len(table) else None

            # REVELAR / OCULTAR 
            if event == "-REVEAL-":
                if servico is None:
                    sg.popup("Selecione uma linha para revelar a senha.", title="Atenção")
                    continue
                if servico in self.revealed:
                    self.revealed.discard(servico)
                else:
                    self.revealed.add(servico)
                window["-TABLE-"].update(values=self.helper._build_table())

            # REMOVER
            if event == "-DELETE-":
                if servico is None:
                    sg.popup("Selecione uma linha para remover.", title="Atenção")
                    continue
                if sg.popup_yes_no(f"Remover a senha de '{servico}'?", title="Confirmar") != "Yes":
                    continue
                if self.helper._delete_password(servico):
                    self.helper._reload_passwords()
                    self.revealed.discard(servico)
                    window["-TABLE-"].update(values=self.helper._build_table())
                    sg.popup("Senha removida com sucesso!", title="Sucesso")
                else:
                    sg.popup("Falha ao remover a senha no banco.", title="Erro")

            # EDITAR
            if event == "-EDIT-":
                if servico is None:
                    sg.popup("Selecione uma linha para editar.", title="Atenção")
                    continue
                info = self.helper.passwords.get(servico, {})
                updated = UpdateLayout(self.password_controller).show_update_window(
                    servico,
                    info.get("credencial", ""),
                    info.get("password", ""),
                    info.get("notes", ""),
                    self.user_id,
                )
                if updated:
                    self.helper._reload_passwords()
                    window["-TABLE-"].update(values=self.helper._build_table())

            # SALVAR NOVA SENHA
            if event == "-SAVE-":
                servico_form = values["-SERVICO-"].strip()
                credencial_form = values["-CREDENCIAL-"].strip()
                passwd_form = values["-PASS-"]
                notes_form = values["-NOTES-"].strip()

                if not servico_form or not passwd_form:
                    sg.popup("Preencha pelo menos Serviço e Senha.", title="Atenção")
                    continue

                if self.helper._save_password(servico_form, credencial_form, passwd_form, notes_form):
                    self.helper._reload_passwords()
                    self.helper._clear_form(window)
                    window["-TABLE-"].update(values=self.helper._build_table())
                    sg.popup("Senha salva com sucesso!", title="Sucesso")
                else:
                    sg.popup("Falha ao salvar a senha.", title="Erro")

        window.close()


if __name__ == "__main__":
    DashboardLayout().run()
    