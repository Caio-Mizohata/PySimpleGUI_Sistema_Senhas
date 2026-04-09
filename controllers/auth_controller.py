import PySimpleGUI as sg
from layouts.login_layout import login_layout


def open_login(password_manager):
    layout = login_layout()
    window = sg.Window("Login", layout)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "-EXIT-"):
            window.close()
            return False
        if event == "-LOGIN-":
            user = values.get("-USER-")
            pw = values.get("-PASS-")
            if user and pw:
                # Para exemplo, não fazemos verificação avançada
                window.close()
                return True
            else:
                sg.popup("Preencha usuário e senha")
