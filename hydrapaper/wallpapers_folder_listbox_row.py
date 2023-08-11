from gi.repository import Gtk
from hydrapaper.folder_store import FolderObj
from hydrapaper.confManager import ConfManager


class WallpapersFolderListBoxRow(Gtk.ListBoxRow):
    def __init__(self, folderobj: FolderObj):
        super().__init__()

        self.confman = ConfManager()
        self.folderobj = folderobj
        self.folder_path = self.folderobj.path

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.label = Gtk.Label()
        self.switch = Gtk.CheckButton()

        self.set_label_text()
        self.label.set_margin_start(12)
        self.label.set_margin_end(6)
        self.label.set_halign(Gtk.Align.START)

        self.switch.set_active(self.folderobj.folder_active)
        self.switch.set_margin_start(6)
        self.switch.set_margin_end(12)

        self.box.append(self.label)
        self.label.set_hexpand(True)
        self.box.append(self.switch)
        self.box.set_margin_top(6)
        self.box.set_margin_bottom(6)

        self.value = self.folder_path

        self.set_child(self.box)
        self.switch_toggled_handler_id = self.switch.connect(
            'toggled', self.on_switch_state_set
        )
        self.folderobj_notify_active_id = self.folderobj.connect(
            'notify::folder-active', self.on_folder_notify_active
        )
        self.confman.connect(
            'hydrapaper_set_folders_popover_labels',
            self.set_label_text
        )

    def on_folder_notify_active(self, *_):
        with self.switch.handler_block(self.switch_toggled_handler_id):
            self.switch.set_active(self.folderobj.folder_active)

    def on_switch_state_set(self, switch):
        with self.folderobj.handler_block(self.folderobj_notify_active_id):
            state = self.switch.get_active()
            self.folderobj.folder_active = state

    def set_label_text(self, *_):
        self.label.set_text(
            str(self.folderobj.path)
            if self.confman.conf['folders_popover_full_path']
            else str(self.folderobj.path.name)
        )
