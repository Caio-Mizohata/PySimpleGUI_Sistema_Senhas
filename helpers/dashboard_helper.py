import asyncio
import PySimpleGUI as sg
from controllers.password_controller import PasswordController

class DashboardHelper:
    def __init__(self, password_controller: PasswordController = None, user_id: int = None):
        self.password_controller = password_controller
        self.user_id = user_id
        self.revealed: set = set()
        self.passwords: dict = {}


    def _normalize(self) -> dict:
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


    def _save_password(self, servico, credencial, password, notes) -> bool:
        try:
            return asyncio.run(self.password_controller.save_password(servico, credencial, password, notes, self.user_id))
        except Exception as e:
            sg.popup(f"Erro ao salvar: {e}", title="Erro")
        return False


    def _delete_password(self, servico) -> bool:
        try:
            return bool(asyncio.run(self.password_controller.delete_password(servico, self.user_id)))
        except Exception as e:
            sg.popup(f"Erro ao remover: {e}", title="Erro")
        return False
    
    def revealed_passwords(self, servico):
        if servico is None:
            sg.popup("Selecione uma linha para revelar a senha.", title="Atenção")
            return
        if servico in self.revealed:
            self.revealed.discard(servico)
        else:
            self.revealed.add(servico)
        return self.revealed
    