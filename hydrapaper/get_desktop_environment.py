from os import environ as Env


def get_desktop_environment():
    desktop_environment = ''
    candidates = [
         'XDG_SESSION_DESKTOP', 'DESKTOP_SESSION', 'XDG_CURRENT_DESKTOP'
    ]
    for c in candidates:
        desktop_environment = Env.get(c)
        if not not desktop_environment:
            break
    if not desktop_environment:
        desktop_environment = ''
    return desktop_environment.lower()
