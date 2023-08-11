from os import environ
from os.path import isfile


def is_flatpak() -> bool:
    return (
        'XDG_RUNTIME_DIR' in environ.keys() and
        isfile(f'{environ["XDG_RUNTIME_DIR"]}/flatpak-info')
    )
