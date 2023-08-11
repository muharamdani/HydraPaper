from subprocess import PIPE, Popen
from gi.repository import Gio
from hydrapaper.is_flatpak import is_flatpak


def get_gnome_dark_mode() -> bool:
    if is_flatpak():
        out, _ = Popen([
            'flatpak-spawn',
            '--host',
            'gsettings',
            'get',
            'org.gnome.desktop.interface',
            'color-scheme'
        ], stdout=PIPE).communicate()
        return out.decode().strip().strip("'") == 'prefer-dark'
    gs = Gio.Settings.new('org.gnome.desktop.interface')
    scheme = str(gs.get_string('color-scheme'))
    return scheme == 'prefer-dark'
