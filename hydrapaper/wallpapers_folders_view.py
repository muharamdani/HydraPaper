from gettext import gettext as _
from pathlib import Path
from gi.repository import Gtk
from hydrapaper.folder_store import FolderObj
from hydrapaper.folder_store import FolderStore
from hydrapaper.confManager import ConfManager
from hydrapaper.wallpapers_folder_listbox_row import WallpapersFolderListBoxRow
from os.path import isdir


@Gtk.Template(
    resource_path='/org/gabmus/hydrapaper/ui/wallpapers_folders_view.ui'
)
class HydraPaperWallpapersFoldersView(Gtk.Box):
    __gtype_name__ = 'WallpapersFoldersView'
    listbox: Gtk.ListBox = Gtk.Template.Child()
    add_btn: Gtk.Button = Gtk.Template.Child()
    del_btn: Gtk.Button = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.parent_win = window
        self.folder_store = FolderStore()
        self.listbox.bind_model(self.folder_store, self.__create_row, None)

    def __create_row(self, folderobj: FolderObj, *_) -> Gtk.ListBoxRow:
        row = WallpapersFolderListBoxRow(folderobj)
        folderobj.connect(
            'notify::folder-active', self.on_folder_active_changed
        )
        return row

    @Gtk.Template.Callback()
    def on_listbox_row_selected(self, listbox, row):
        self.del_btn.set_sensitive(
            not not row and self.add_btn.get_sensitive()
        )

    def on_folder_active_changed(self, folderobj, _):
        for i, p in enumerate(self.confman.conf['wallpapers_paths']):
            if p['path'] == str(folderobj.path):
                self.confman.conf['wallpapers_paths'][i][
                    'active'
                ] = folderobj.folder_active
                self.confman.emit(
                    'hydrapaper_show_hide_wallpapers', ''
                )
                self.confman.save_conf()
                break

    @Gtk.Template.Callback()
    def on_add_btn_clicked(self, btn):
        self.fc_dialog = Gtk.FileChooserNative(
            title=_('Add wallpaper folders'),
            transient_for=self.parent_win,
            modal=True,
            select_multiple=True,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )

        def on_response(dialog, res):
            if res == Gtk.ResponseType.ACCEPT:
                for fpath in dialog.get_files():
                    fpath = fpath.get_path()
                    if isdir(fpath):
                        self.confman.conf['wallpapers_paths'].append({
                            'path': fpath,
                            'active': True
                        })
                        self.folder_store.add_folder(FolderObj(Path(fpath)))
                self.confman.save_conf()
                self.confman.populate_wallpapers()
                self.confman.emit(
                    'hydrapaper_populate_wallpapers', ''
                )

        self.fc_dialog.connect('response', on_response)
        self.fc_dialog.show()

    @Gtk.Template.Callback()
    def on_del_btn_clicked(self, btn):
        row = self.listbox.get_selected_row()
        if not row or not row.folder_path:
            return
        c_paths = self.confman.conf['wallpapers_paths']
        for i, p in enumerate(c_paths):
            if p['path'] == str(row.folder_path):
                self.folder_store.remove_folder_by_path(p['path'])
                c_paths.pop(i)
                self.confman.conf['wallpapers_paths'] = c_paths
                self.confman.populate_wallpapers()
                break
        for i, fav in enumerate(self.confman.conf['favorites']):
            if str(row.folder_path) in fav:
                self.confman.conf['favorites'].pop(i)
        self.confman.save_conf()

    def set_all_enabled(self, state):
        for i, __ in enumerate(self.confman.conf['wallpapers_paths']):
            self.confman.conf['wallpapers_paths'][i]['active'] = state
        for folderobj in self.folder_store.list_store:
            if not folderobj:
                continue
            folderobj.folder_active = state
        self.confman.emit('hydrapaper_show_hide_wallpapers', '')
        self.confman.save_conf()

    @Gtk.Template.Callback()
    def on_activate_all_btn_clicked(self, __):
        self.set_all_enabled(True)

    @Gtk.Template.Callback()
    def on_deactivate_all_btn_clicked(self, __):
        self.set_all_enabled(False)
