import PySimpleGUI as sg
import asyncio
from controllers.password_controller import PasswordController


class DashboardLayout:
    def __init__(self,password_controller: PasswordController = None,user_id: int = None,):
        self.password_controller = password_controller
        if not self.password_controller:
            raise ValueError(
                "PasswordController obrigatório para operar sem modo local."
            )
        self.user_id = user_id
        self.revealed: set = set()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalize(self) -> dict:
        """Garante que cada valor seja um dict com 'email' e 'password'."""
        normalized = {}
        for servico, val in self.passwords.items():
            if isinstance(val, dict):
                normalized[servico] = val
            else:
                normalized[servico] = {"email": "", "password": str(val)}
        return normalized

    def _build_table(self) -> list[list[str]]:
        data = self._normalize()
        rows = []
        for servico, info in data.items():
            pw_display = info["password"] if servico in self.revealed else "••••••••••"
            rows.append(
                [
                    servico,
                    info.get("credencial", ""),
                    pw_display,
                    info.get("notes", ""),
                ]
            )
        return rows

    def _reload_passwords(self):
        try:
            self.passwords = asyncio.run(
                self.password_controller.get_all_passwords(self.user_id)
            )
        except Exception as e:
            sg.popup(f"Erro ao carregar senhas: {e}", title="Erro")
            self.passwords = {}

    def _clear_form(self, window):
        for k in ("-SERVICO-", "-CREDENCIAL-", "-NOTES-", "-PASS-"):
            window[k].update("")

    def _save_password(self, servico: str, credencial: str, password: str, notes: str) -> bool:
        try:
            return asyncio.run(
                self.password_controller.save_password(
                    servico, credencial, password, notes, self.user_id
                )
            )
        except Exception as e:
            sg.popup(f"Erro ao salvar: {e}", title="Erro")
            return False

    def _delete_password(self, servico: str) -> bool:
        delete_fn = getattr(self.password_controller, "delete_password", None)
        if delete_fn is None:
            sg.popup(
                "Método 'delete_password' não encontrado no PasswordController.",
                title="Erro",
            )
            return False
        try:
            try:
                result = asyncio.run(delete_fn(servico, self.user_id))
            except TypeError:
                result = asyncio.run(delete_fn(servico))
            return True if result is None else bool(result)
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
                    col_widths=[16, 18, 14, 14, 22],
                    num_rows=12,
                    enable_events=True,
                    select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                    expand_x=True,
                    expand_y=True,
                )
            ],
            [
                sg.Button("👁  Revelar / Ocultar", key="-REVEAL-"),
                sg.Button("🗑  Remover", key="-DELETE-"),
            ],
        ]

    def _form_panel(self) -> list:
        return [
            [sg.Text("Adicionar senha", font=("Helvetica", 11, "bold"))],
            [sg.HorizontalSeparator()],
            [sg.Text("Serviço   ", size=6), sg.Input(key="-SERVICO-", size=22)],
            [sg.Text("Credencial", size=6), sg.Input(key="-CREDENCIAL-", size=22)],
            [
                sg.Text("Senha  ", size=6),
                sg.Input(password_char="*", key="-PASS-", size=22),
            ],
            [sg.Text("Notas  ", size=6), sg.Multiline(key="-NOTES-", size=(22, 3))],
            [sg.HorizontalSeparator()],
            [sg.Push(), sg.Button("💾  Salvar", key="-SAVE-", size=12), sg.Push()],
        ]

    def _layout(self) -> list:
        return [
            [
                sg.Text("🔐 Dashboard", font=("Helvetica", 14, "bold")),
                sg.Push(),
                sg.Button("Sair", key="-EXIT-", size=8),
            ],
            [sg.HorizontalSeparator()],
            [
                # Coluna esquerda: tabela de senhas
                sg.Column(
                    self._table_panel(),
                    expand_x=True,
                    expand_y=True,
                    vertical_alignment="top",
                ),
                sg.VerticalSeparator(),
                # Coluna direita: formulário de nova senha
                sg.Column(
                    self._form_panel(),
                    size=(230, None),
                    vertical_alignment="top",
                    pad=(10, 0),
                ),
            ],
        ]

    # ------------------------------------------------------------------
    # Event loop
    # ------------------------------------------------------------------

    def run(self):
        # Carrega senhas do controller antes de construir a janela
        self._reload_passwords()

        window = sg.Window(
            "Dashboard – Gerenciador de Senhas",
            self._layout(),
            size=(760, 400),
            resizable=True,
            finalize=True,
        )

        while True:
            event, values = window.read()

            if event in (sg.WIN_CLOSED, "-EXIT-"):
                break

            # ── REVELAR / OCULTAR ──────────────────────────────────────
            if event == "-REVEAL-":
                selected = values.get("-TABLE-", [])
                if not selected:
                    sg.popup(
                        "Selecione uma linha para revelar a senha.", title="Atenção"
                    )
                    continue
                table = self._build_table()
                row_idx = selected[0]
                if 0 <= row_idx < len(table):
                    servico = table[row_idx][0]
                    confirm = sg.popup_yes_no(
                        f"{'Revelar' if servico not in self.revealed else 'Ocultar'} a senha de '{servico}'?",
                        title="Confirmar",
                    )
                    if confirm != "Yes":
                        continue

                    if servico in self.revealed:
                        self.revealed.remove(servico)
                    else:
                        self.revealed.add(servico)
                    window["-TABLE-"].update(values=self._build_table())

            # ── REMOVER ────────────────────────────────────────────────
            if event == "-DELETE-":
                selected = values.get("-TABLE-", [])
                if not selected:
                    sg.popup("Selecione uma linha para remover.", title="Atenção")
                    continue

                table = self._build_table()
                row_idx = selected[0]

                if 0 <= row_idx < len(table):
                    servico = table[row_idx][0]
                    confirm = sg.popup_yes_no(
                        f"Remover a senha de '{servico}'?", title="Confirmar"
                    )
                    if confirm == "Yes":
                        ok = self._delete_password(servico)

                        if ok:
                            # sempre recarrega via controller
                            self._reload_passwords()
                            self.revealed.discard(servico)
                            window["-TABLE-"].update(values=self._build_table())
                            sg.popup("Senha removida com sucesso!", title="Sucesso")
                        else:
                            sg.popup("Falha ao remover a senha no banco.", title="Erro")

            # ── SALVAR NOVA SENHA ──────────────────────────────────────
            if event == "-SAVE-":

                servico = values["-SERVICO-"].strip()
                credencial = values["-CREDENCIAL-"].strip()
                passwd = values["-PASS-"]
                notes = values.get("-NOTES-", "").strip()

                if not servico or not passwd:
                    sg.popup("Preencha pelo menos Serviço e Senha.", title="Atenção")
                    continue

                ok = self._save_password(servico, credencial, passwd, notes)

                if ok:
                    # recarrega sempre via controller
                    self._reload_passwords()
                    self._clear_form(window)
                    window["-TABLE-"].update(values=self._build_table())
                    sg.popup("Senha salva com sucesso!", title="Sucesso")
                else:
                    sg.popup("Falha ao salvar a senha.", title="Erro")

        window.close()


if __name__ == "__main__":

    DashboardLayout.run()
