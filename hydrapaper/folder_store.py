from pathlib import Path
from typing import List, Union
from gi.repository import Gtk, Gio, GObject
from hydrapaper.confManager import ConfManager


class FolderObj(GObject.Object):
    __gtype_name__ = 'FolderObj'

    def __init__(self, path: Union[Path, str], active: bool = True):
        if isinstance(path, str):
            path = Path(path)
        assert(path.is_dir())
        assert(path.is_absolute())
        self.path = path
        self.__active = active
        super().__init__()

    @GObject.Property(type=bool, default=False)
    def folder_active(self) -> bool:
        return self.__active

    @folder_active.setter
    def folder_active(self, n_active: bool):
        self.__active = n_active


class FolderStore(Gtk.SortListModel):
    def __init__(self):
        self.confman = ConfManager()
        self.sorter = Gtk.CustomSorter()
        self.sorter.set_sort_func(self.__sort_func)
        self.list_store = Gio.ListStore(item_type=FolderObj)
        super().__init__(model=self.list_store, sorter=self.sorter)
        self.populate()

    def populate(self):
        self.empty()
        for folder in self.confman.conf['wallpapers_paths']:
            obj = FolderObj(folder['path'], folder['active'])
            self.add_folder(obj)

    def __sort_func(self, f1: FolderObj, f2: FolderObj, *_) -> int:
        return -1 if f1.path < f2.path else 1

    def invalidate_sort(self):
        self.sorter.set_sort_func(self.__sort_func)

    def empty(self):
        self.list_store.remove_all()

    def add_folder(self, folder: FolderObj):
        self.list_store.append(folder)

    def remove_folder_by_path(self, target: Union[Path, str]):
        if isinstance(target, str):
            target = Path(target)
        for i, folder in enumerate(self.list_store):
            if not folder:
                continue
            if folder.path == target:
                self.list_store.remove(i)
                return

    def remove_folder(self, folder: FolderObj):
        self.remove_folder_by_path(folder.path)

    def get_active_folders(self) -> List[Path]:
        return [
            folder.path for folder in self.list_store
            if folder and folder.folder_active
        ]
