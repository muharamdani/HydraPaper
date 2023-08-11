from hydrapaper.is_flatpak import is_flatpak
from .singleton import Singleton
from gi.repository import GObject, GLib
from pathlib import Path
from os.path import isfile, isdir
from .is_image import is_image
from os import makedirs, listdir, system
from os import environ as Env
import json
import os
from threading import Thread

pictures_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
if not pictures_dir:
    system('xdg-user-dirs-update')
    pictures_dir = GLib.get_user_special_dir(
        GLib.UserDirectory.DIRECTORY_PICTURES
    )
    if not pictures_dir:
        pictures_dir = f'{Env.get("HOME")}/Pictures'


class ConfManagerSignaler(GObject.Object):
    __gsignals__ = {
        'dark_mode_changed': (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (str,)
        ),
        'hydrapaper_flowbox_wallpaper_selected': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'hydrapaper_populate_wallpapers': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'hydrapaper_show_hide_wallpapers': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'hydrapaper_set_folders_popover_labels': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'hydrapaper_reload_monitor_thumbs': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'hydrapaper_spanned_mode_changed': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        )
    }


class ConfManager(metaclass=Singleton):

    BASE_SCHEMA = {
        'wallpapers_paths': [
            {
                'path': pictures_dir,
                'active': True
            }
        ],
        'dark_mode': False,
        'monitors': {},
        'favorites': [],
        'folders_popover_full_path': False,
        'big_monitor_thumbnails': True,
        'random_wallpapers_names': False,
        'spanned_mode': False,
        'windowsize': {
            'width': 600,
            'height': 400
        },
        'enable_daemon': False,
        'last_wps': {
            'spanned': False,
            'wps': {}
        },  # saved when applying wallpapers, retrieved by daemon
        'Daemon': {
            'wallpaper_rotation_enabled': False,
            'wallpaper_rotation_sleep_time': 30,
            'rotating_wallpapers': []  # list of lists of rotating wallpapers
        }
    }

    def __init__(self):
        self.signaler = ConfManagerSignaler()
        self.emit = self.signaler.emit
        self.connect = self.signaler.connect

        self.config_home = os.getenv('XDG_CONFIG_HOME', f'{Env.get("HOME")}/.config')
        self.cache_home = os.getenv('XDG_CACHE_HOME', f'{Env.get("HOME")}/.cache')
        self.path = Path(
            f'{self.config_home}/org.gabmus.hydrapaper.json'
        )
        self.cache_path = f'{self.cache_home}/org.gabmus.hydrapaper'
        self.thumbs_cache_path = f'{self.cache_path}/thumbnails/'

        if isfile(str(self.path)):
            try:
                with open(self.path) as fd:
                    self.conf = json.loads(fd.read())
                    fd.close()
                # verify that the file has all of the schema keys
                for k in self.BASE_SCHEMA.keys():
                    if k not in self.conf.keys():
                        if type(self.BASE_SCHEMA[k]) in [list, dict]:
                            self.conf[k] = self.BASE_SCHEMA[k].copy()
                        else:
                            self.conf[k] = self.BASE_SCHEMA[k]

                # verify that monitors is a dict of dicts
                if len(self.conf['monitors']) > 0:
                    for m_name in self.conf['monitors']:
                        if not isinstance(self.conf['monitors'][m_name], dict):
                            if isinstance(self.conf['monitors'][m_name], str):
                                self.conf['monitors'][m_name] = {
                                    'wallpaper': self.conf['monitors'][m_name],
                                    'mode': 'zoom'
                                }
                            else:
                                self.conf['monitors'][m_name] = {
                                    'wallpaper': '',
                                    'mode': 'zoom'
                                }
            except Exception:
                self.conf = self.BASE_SCHEMA.copy()
                self.save_conf()
        else:
            self.conf = self.BASE_SCHEMA.copy()
            self.save_conf()

        for p in [self.cache_path, self.thumbs_cache_path]:
            if not isdir(p):
                makedirs(p)

        self.windows_to_restore = []

        self.wallpapers = []
        self.populate_wallpapers()

    def save_conf(self):
        with open(self.path, 'w') as fd:
            fd.write(json.dumps(self.conf))
            fd.close()

    def save_conf_async(self):
        Thread(target=self.save_conf).start()

    def populate_wallpapers(self):
        self.wallpapers = []
        for index, folder in enumerate(self.conf['wallpapers_paths']):
            if isdir(folder['path']):
                for f in listdir(folder['path']):
                    f_path = f'{folder["path"]}/{f}'
                    if is_image(f_path):
                        self.wallpapers.append(f_path)
            else:
                self.conf['wallpapers_paths'].pop(index)
        self.emit(
            'hydrapaper_populate_wallpapers',
            'notimportant'
        )
