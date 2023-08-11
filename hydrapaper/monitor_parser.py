from gettext import gettext as _
from gi.repository import Gdk
from subprocess import run, PIPE
import json
from hydrapaper.get_desktop_environment import get_desktop_environment
from hydrapaper.confManager import ConfManager
from hydrapaper.is_flatpak import is_flatpak
from hydrapaper.wallpaper_merger import get_combined_resolution
from os import environ as Env
import dbus


confman = ConfManager()


class Monitor:
    def __init__(
            self,
            width,
            height,
            scaling,
            offset_x,
            offset_y,
            index,
            name,
            mode='zoom',
            primary=False,
            spanned=False
    ):
        self.width = int(width)
        self.height = int(height)
        self.scaling = int(scaling)
        self.primary = primary
        self.offset_x = int(offset_x)
        self.offset_y = int(offset_y)
        self.index = index
        self.name = name
        self.mode = mode
        self.wallpaper = None
        self.spanned = spanned

        if self.name in confman.conf['monitors'].keys():
            self.wallpaper = \
                confman.conf['monitors'][self.name]['wallpaper']
            self.mode = confman.conf['monitors'][self.name]['mode']

    def __repr__(self):
        return (
            'HydraPaper Monitor Object: '
            f'Name: {self.name}; '
            f'Resolution: {self.width} x {self.height}; '
            f'Scaling: {self.scaling}; '
            f'Offset: {self.offset_x} x {self.offset_y}; '
            f'Wallpaper path: {self.wallpaper}; '
            f'Mode: {self.mode}; '
            f'Spanned: {self.spanned}.'
        )


def build_monitors_from_swaymsg():
    cmd = 'swaymsg -rt get_outputs'
    if is_flatpak():
        cmd = 'flatpak-spawn --host ' + cmd
    res = run(cmd.split(' '), stdout=PIPE)
    outputs = json.loads(res.stdout.decode())
    monitors = [
        Monitor(
            out['rect']['width'],
            out['rect']['height'],
            out['scale'],
            out['rect']['x'],
            out['rect']['y'],
            i,
            out['name'],
            'zoom',
            out['primary']
        ) for i, out in enumerate(outputs)
    ]
    return monitors


def get_layout_mode():
    """
        Scale factor can be either 1 on X11, or another value if the whole
        desktop on Wayland where it's treated as if every monitor has the
        highest dpi mode available
    """
    desktop_environment = get_desktop_environment()
    if (
            Env.get('XDG_SESSION_TYPE') != 'x11' and
            desktop_environment in ['gnome', 'ubuntu-wayland']
    ):
        bus = dbus.SessionBus()
        object_display_config = bus.get_object(
            'org.gnome.Mutter.DisplayConfig',
            '/org/gnome/Mutter/DisplayConfig'
        )
        interface_display_config = dbus.Interface(
            object_display_config,
            dbus_interface='org.gnome.Mutter.DisplayConfig'
        )
        state = interface_display_config.GetCurrentState()
        return int(state[3].get('layout-mode'))
    else:
        return 1


def build_monitors_from_gdk():
    monitors = []
    num_monitors = 0
    max_scale_factor = 0
    try:
        display = Gdk.Display.get_default()
        monitors = list(display.get_monitors())
        num_monitors = len(monitors)
    except Exception:
        print(_('Error parsing monitors (Gdk)'))
        import traceback
        traceback.print_exc()
        monitors = None
        return

    if get_layout_mode() == 1:
        max_scale_factor = max([m.get_scale_factor() for m in monitors])
    else:
        max_scale_factor = 1

    res = list()
    for i in range(num_monitors):
        rect = monitors[i].get_geometry()
        res.append(Monitor(
            rect.width, rect.height,
            max_scale_factor,
            rect.x, rect.y,
            i,
            f'Monitor {i} ({monitors[i].get_model()})',
            'zoom',
            i == 0  # first monitor will be the primary, doesn't mean much
        ))
    return res


def build_monitors_autodetect():
    desktop_environment = get_desktop_environment()
    if desktop_environment == 'sway':
        return build_monitors_from_swaymsg()
    else:
        return build_monitors_from_gdk()


def build_combined_spanned_monitor(monitors=None):
    if monitors is None:
        monitors = build_monitors_autodetect()
    return Monitor(
        *get_combined_resolution(monitors),
        1, 0, 0, 0,
        _('Combined spanned monitor'),
        'zoom',
        True, True
    )
