from gettext import gettext as _
from gi.repository import Gtk
from os.path import isfile
from hydrapaper.confManager import ConfManager


class SlideshowListboxRow(Gtk.ListBoxRow):
    def __init__(self, pictures=[], **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.pictures = pictures
        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
            margin_top=6, margin_bottom=6, margin_start=6, margin_end=6
        )
        self.pic_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True
        )
        self.btn_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            margin_start=12, margin_end=12,
            valign=Gtk.Align.CENTER, vexpand=True
        )

        self.btn_box.get_style_context().add_class('linked')
        self.move_up_btn = Gtk.Button(
            icon_name='go-up-symbolic',
            tooltip_text=_('Move up')
        )
        self.move_up_btn.connect('clicked', self.on_move_up_clicked)
        self.remove_btn = Gtk.Button(
            icon_name='list-remove-symbolic',
            tooltip_text=_('Remove')
        )
        self.remove_btn.connect('clicked', self.on_remove_clicked)
        self.move_down_btn = Gtk.Button(
            icon_name='go-down-symbolic',
            tooltip_text=_('Move down')
        )
        self.move_down_btn.connect('clicked', self.on_move_down_clicked)
        self.btn_box.append(self.move_up_btn)
        self.btn_box.append(self.remove_btn)
        self.btn_box.append(self.move_down_btn)

        self.main_box.append(self.pic_box)
        self.main_box.append(self.btn_box)

        self.set_child(self.main_box)

        self.set_pictures()

    def repopulate_listbox(self):
        self.get_parent().populate()

    def find_index_in_conf(self):
        for i, pics in enumerate(
                self.confman.conf['Daemon']['rotating_wallpapers']
        ):
            if [p['wallpaper'] for p in pics] == self.pictures:
                return i
        return -1

    def on_move_up_clicked(self, *args):
        i = self.find_index_in_conf()
        if i <= 0:
            return
        x = self.confman.conf['Daemon']['rotating_wallpapers'].pop(i)
        self.confman.conf['Daemon']['rotating_wallpapers'].insert(i-1, x)
        self.confman.save_conf_async()
        self.repopulate_listbox()

    def on_move_down_clicked(self, *args):
        i = self.find_index_in_conf()
        if i+1 >= len(self.confman.conf['Daemon']['rotating_wallpapers']):
            return
        x = self.confman.conf['Daemon']['rotating_wallpapers'].pop(i)
        self.confman.conf['Daemon']['rotating_wallpapers'].insert(i+1, x)
        self.confman.save_conf_async()
        self.repopulate_listbox()

    def on_remove_clicked(self, *args):
        i = self.find_index_in_conf()
        if i >= 0:
            self.confman.conf['Daemon']['rotating_wallpapers'].pop(i)
            self.confman.save_conf_async()
        self.repopulate_listbox()

    def empty_pic_box(self):
        child = self.pic_box.get_first_child()
        while child is not None:
            self.pic_box.remove(child)
            child = self.pic_box.get_first_child()

    def set_pictures(self, pictures=None):
        self.empty_pic_box()
        if pictures is not None:
            self.pictures = pictures
        for pic in self.pictures:
            if not isfile(pic):
                continue
            pic_w = Gtk.Picture.new_for_filename(pic)
            self.pic_box.append(pic_w)
