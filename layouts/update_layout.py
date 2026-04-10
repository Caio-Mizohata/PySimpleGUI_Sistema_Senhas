import asyncio
import PySimpleGUI as sg
from controllers.password_controller import PasswordController


class UpdateLayout:
    def __init__(self, password_controller: PasswordController):
        self.password_controller = password_controller

    def _build_layout(self, servico: str, credencial: str, password: str, notes: str) -> list:
        return [
            [sg.Text(f"Editar credencial — {servico}", font=("Helvetica", 12, "bold"))],
            [sg.HorizontalSeparator()],
            [sg.Text("Serviço",    size=10), sg.Input(servico,          key="-U-SERVICO-", disabled=True, size=40)],
            [sg.Text("Credencial", size=10), sg.Input(credencial or "", key="-U-CRED-",    size=40)],
            [sg.Text("Senha",      size=10), sg.Input(password or "",   key="-U-PASS-",    size=40)],
            [sg.Text("Notas",      size=10), sg.Multiline(notes or "",  key="-U-NOTES-",   size=(50, 6))],
            [sg.HorizontalSeparator()],
            [sg.Push(), sg.Button("💾  Salvar", key="-U-SAVE-"), sg.Button("Cancelar", key="-U-CANCEL-"), sg.Push()],
        ]

    def show_update_window(self,servico: str,credencial: str,password: str,notes: str,user_id: int,) -> bool:
        window = sg.Window("Editar credencial",self._build_layout(servico, credencial, password, notes), modal=True, finalize=True,)
        try:
            while True:
                event, values = window.read()

                if event in (sg.WIN_CLOSED, "-U-CANCEL-"):
                    return False

                if event == "-U-SAVE-":
                    new_cred  = values["-U-CRED-"].strip()
                    new_pass  = values["-U-PASS-"]
                    new_notes = values["-U-NOTES-"].strip()

                    if not new_cred or not new_pass:
                        sg.popup("Preencha pelo menos Credencial e Senha.", title="Atenção")
                        continue

                    try:
                        ok = asyncio.run(self.password_controller.update_password(servico, new_cred, new_pass, new_notes, user_id))
                    except Exception as e:
                        sg.popup(f"Erro ao atualizar: {e}", title="Erro")
                        continue

                    if ok:
                        sg.popup("Credencial atualizada com sucesso!", title="Sucesso")
                        return True

                    sg.popup("Falha ao atualizar credencial.", title="Erro")
        finally:
            window.close()
            