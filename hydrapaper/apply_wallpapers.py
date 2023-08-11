from threading import Thread
from gi.repository import GLib
from hashlib import sha256
from os.path import isfile
from hydrapaper.wallpaper_merger import (
    set_wallpaper_gnome,
    set_wallpaper_cinnamon,
    set_wallpaper_mate,
    set_wallpaper_sway,
    multi_setup_pillow,
    # cut_image
)
from hydrapaper.confManager import ConfManager
from hydrapaper.get_desktop_environment import get_desktop_environment


def widgets_set_sensitive(widgets, state: bool):
    for w in widgets:
        w.set_sensitive(state)


def _apply_wallpapers_worker(
    monitors, widgets_to_freeze=[],
    force_random_name=False,
    set_dark=False
):
    confman = ConfManager()
    random_name = confman.conf['random_wallpapers_names'] or force_random_name
    desktop_environment = get_desktop_environment()
    set_wallpaper = lambda *args: set_wallpaper_gnome(*args, set_dark=set_dark)
    if desktop_environment == 'mate':
        set_wallpaper = set_wallpaper_mate
    elif desktop_environment == 'cinnamon':
        set_wallpaper = set_wallpaper_cinnamon
    elif desktop_environment == 'sway':
        set_wallpaper_sway(monitors)
        GLib.idle_add(widgets_set_sensitive, widgets_to_freeze, True)
        return
    # add other DE cases as `elif` here
    wp_fname = 'merged_wallpaper' + ('_dark' if set_dark else '')
    if random_name:
        wp_fname = sha256(
            '_'.join([m.__repr__() for m in monitors]).encode()
        ).hexdigest()
    save_path = '{0}/{1}.png'.format(confman.cache_path, wp_fname)
    if not random_name or not isfile(save_path):
        multi_setup_pillow(monitors, save_path)
    set_wallpaper(save_path)
    GLib.idle_add(widgets_set_sensitive, widgets_to_freeze, True)


def apply_wallpapers(
        monitors, widgets_to_freeze=[], force_random_name=False,
        skip_save=False, set_dark=None
):
    for m in monitors:
        if m.wallpaper is None:
            return
    t = Thread(
        group=None,
        target=_apply_wallpapers_worker,
        name=None,
        args=(monitors, widgets_to_freeze, force_random_name, set_dark)
    )
    widgets_set_sensitive(widgets_to_freeze, False)
    t.start()
    if not skip_save:
        confman = ConfManager()
        confman.conf['last_wps'] = {
            'spanned': monitors[0].spanned,
            'wps': {
                m.name: {'wp': m.wallpaper, 'mode': m.mode} for m in monitors
            }
        }
        confman.save_conf_async()
