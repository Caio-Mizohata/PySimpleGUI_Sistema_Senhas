import asyncio

import PySimpleGUI as sg

from controllers.password_controller import PasswordController
from layouts.update_layout import UpdateLayout


class DashboardLayout:
    def __init__(self, password_controller: PasswordController = None, user_id: int = None):
        self.password_controller = password_controller
        self.user_id = user_id
        self.revealed: set = set()
        self.passwords: dict = {}        

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalize(self) -> dict:
        # Garante que cada valor seja um dicionário
        normalized = {}
        for servico, val in self.passwords.items():
            if isinstance(val, dict):
                normalized[servico] = val
            else:
                normalized[servico] = {"credencial": "", "password": str(val), "notes": ""}
        return normalized

    def _build_table(self) -> list[list[str]]:
        rows = []
        for servico, info in self._normalize().items():
            pw_display = info["password"] if servico in self.revealed else "••••••••••"
            rows.append([servico, info.get("credencial", ""), pw_display, info.get("notes", "")])
        return rows

    def _reload_passwords(self):
        try:
            self.passwords = asyncio.run(self.password_controller.get_all_passwords(self.user_id))
        except Exception as e:
            sg.popup(f"Erro ao carregar senhas: {e}", title="Erro")

    def _clear_form(self, window):
        for k in ("-SERVICO-", "-CREDENCIAL-", "-PASS-", "-NOTES-"):
            window[k].update("")

    def _save_password(self, servico: str, credencial: str, password: str, notes: str) -> bool:
        try:
            return asyncio.run(self.password_controller.save_password(servico, credencial, password, notes, self.user_id))
        except Exception as e:
            sg.popup(f"Erro ao salvar: {e}", title="Erro")
            return False

    def _delete_password(self, servico: str) -> bool:
        try:
            return bool(asyncio.run(self.password_controller.delete_password(servico, self.user_id)))
        except Exception as e:
            sg.popup(f"Erro ao remover: {e}", title="Erro")
            return False

    # ------------------------------------------------------------------
    # Layout builders
    # ------------------------------------------------------------------

    def _table_panel(self) -> list:
        return [
            [sg.Text("Senhas salvas", font=("Helvetica", 11, "bold"))],
            [
                sg.Table(
                    values=self._build_table(),
                    headings=["Serviço", "Credencial", "Senha", "Notas"],
                    key="-TABLE-",
                    auto_size_columns=False,
                    col_widths=[16, 18, 14, 22],        # 4 colunas → 4 larguras
                    num_rows=12,
                    enable_events=True,
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    expand_x=True,
                    expand_y=True,
                )
            ],
            [
                sg.Button("🗑 Remover", key="-DELETE-"),
                sg.Button("✏️ Editar", key="-EDIT-"),
                sg.Button("👁 Revelar / Ocultar", key="-REVEAL-"),
            ],
        ]

    def _form_panel(self) -> list:
        return [
            [sg.Text("Adicionar senha", font=("Helvetica", 11, "bold"))],
            [sg.HorizontalSeparator()],
            [sg.Text("Serviço   ", size=10), sg.Input(key="-SERVICO-",    size=22)],
            [sg.Text("Credencial", size=10), sg.Input(key="-CREDENCIAL-", size=22)],
            [sg.Text("Senha     ", size=10), sg.Input(password_char="*", key="-PASS-", size=22)],
            [sg.Text("Notas     ", size=10), sg.Multiline(key="-NOTES-",  size=(22, 3))],
            [sg.HorizontalSeparator()],
            [sg.Push(), sg.Button("💾  Salvar", key="-SAVE-", size=12), sg.Push()],
        ]

    def _layout(self) -> list:
        return [
            [
                sg.Text("Dashboard", font=("Helvetica", 14, "bold")),
                sg.Push(),
                sg.Button("Sair", key="-EXIT-", size=8),
            ],
            [sg.HorizontalSeparator()],
            [
                sg.Column(self._table_panel(), expand_x=True, expand_y=True, vertical_alignment="top"),
                sg.VerticalSeparator(),
                sg.Column(self._form_panel(), size=(260, None), vertical_alignment="top", pad=(10, 0)),
            ],
        ]

    # ------------------------------------------------------------------
    # Event loop
    # ------------------------------------------------------------------

    def run(self):
        self._reload_passwords()

        window = sg.Window(
            "Dashboard – Gerenciador de Senhas",
            self._layout(),
            size=(1000, 570),
            resizable=True,
            finalize=True,
        )

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "-EXIT-"):
                break

            selected = values.get("-TABLE-", [])
            table    = self._build_table()
            row_idx  = selected[0] if selected else -1
            servico  = table[row_idx][0] if 0 <= row_idx < len(table) else None

            # ── REVELAR / OCULTAR ──────────────────────────────────────
            if event == "-REVEAL-":
                if servico is None:
                    sg.popup("Selecione uma linha para revelar a senha.", title="Atenção")
                    continue
                label = "Ocultar" if servico in self.revealed else "Revelar"
                if sg.popup_yes_no(f"{label} a senha de '{servico}'?", title="Confirmar") != "Yes":
                    continue
                self.revealed.discard(servico) if servico in self.revealed else self.revealed.add(servico)
                window["-TABLE-"].update(values=self._build_table())

            # ── REMOVER ────────────────────────────────────────────────
            if event == "-DELETE-":
                if servico is None:
                    sg.popup("Selecione uma linha para remover.", title="Atenção")
                    continue
                if sg.popup_yes_no(f"Remover a senha de '{servico}'?", title="Confirmar") != "Yes":
                    continue
                if self._delete_password(servico):
                    self._reload_passwords()
                    self.revealed.discard(servico)
                    window["-TABLE-"].update(values=self._build_table())
                    sg.popup("Senha removida com sucesso!", title="Sucesso")
                else:
                    sg.popup("Falha ao remover a senha no banco.", title="Erro")

            # ── EDITAR ─────────────────────────────────────────────────
            if event == "-EDIT-":
                if servico is None:
                    sg.popup("Selecione uma linha para editar.", title="Atenção")
                    continue
                info = self.passwords.get(servico, {})
                updated = UpdateLayout(self.password_controller).show_update_window(
                    servico,
                    info.get("credencial", ""),
                    info.get("password", ""),
                    info.get("notes", ""),
                    self.user_id,
                )
                if updated:
                    self._reload_passwords()
                    window["-TABLE-"].update(values=self._build_table())

            # ── SALVAR NOVA SENHA ──────────────────────────────────────
            if event == "-SAVE-":
                servico_form    = values["-SERVICO-"].strip()
                credencial_form = values["-CREDENCIAL-"].strip()
                passwd_form     = values["-PASS-"]
                notes_form      = values["-NOTES-"].strip()

                if not servico_form or not passwd_form:
                    sg.popup("Preencha pelo menos Serviço e Senha.", title="Atenção")
                    continue

                if self._save_password(servico_form, credencial_form, passwd_form, notes_form):
                    self._reload_passwords()
                    self._clear_form(window)
                    window["-TABLE-"].update(values=self._build_table())
                    sg.popup("Senha salva com sucesso!", title="Sucesso")
                else:
                    sg.popup("Falha ao salvar a senha.", title="Erro")

        window.close()


if __name__ == "__main__":
    DashboardLayout().run()
