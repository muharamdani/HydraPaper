from gi.repository import Gtk
from hydrapaper.confManager import ConfManager
from hydrapaper.wallpaper_flowbox_item import WallpaperBox
from hydrapaper.search_bar import HpSearchBar
import pathlib


@Gtk.Template(resource_path='/org/gabmus/hydrapaper/ui/wallpapers_flowbox.ui')
class HydraPaperWallpapersFlowbox(Gtk.ScrolledWindow):
    __gtype_name__ = 'WallpapersFlowbox'
    flowbox = Gtk.Template.Child()

    def __init__(self, searchbar: HpSearchBar, is_favorites=False, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.searchbar = searchbar
        self.is_favorites = is_favorites

        self.confman.connect(
            'hydrapaper_populate_wallpapers',
            self.populate
        )
        self.confman.connect(
            'hydrapaper_show_hide_wallpapers',
            self.show_hide_wallpapers
        )
        self.populate()
        self.flowbox.set_filter_func(self.flowbox_filter_func, None, False)
        self.searchbar.entry.connect('search-changed', self.on_search_changed)

    def on_search_changed(self, *args):
        self.flowbox.invalidate_filter()

    def flowbox_filter_func(self, fb_item, data, notify_destroy):
        search_term = self.searchbar.get_text().strip().lower()
        if self.is_favorites:
            return not search_term or (
                search_term in fb_item.pathlib_path.name.lower() or
                search_term in fb_item.pathlib_path.parent.name.lower() or
                search_term in fb_item.resolution
            )
        return len([
            p for p in self.confman.conf['wallpapers_paths']
            if fb_item.pathlib_path.parent == pathlib.Path(p['path']) and
            p['active'] and (
                not search_term or
                search_term in fb_item.pathlib_path.name.lower() or
                search_term in fb_item.pathlib_path.parent.name.lower() or
                search_term in fb_item.resolution
            )
        ]) > 0

    def populate(self, *args):
        # empty before filling
        while True:
            c = self.flowbox.get_child_at_index(0)
            if c:
                self.flowbox.remove(c)
                # c.destroy()
            else:
                break
        if self.is_favorites:
            for wp in self.confman.wallpapers:
                if wp in self.confman.conf['favorites']:
                    self.flowbox.insert(WallpaperBox(wp), -1)
        else:
            for wp in self.confman.wallpapers:
                self.flowbox.insert(WallpaperBox(wp), -1)
        self.show()
        self.show_hide_wallpapers()

    def show_hide_wallpapers(self, *args):
        self.flowbox.invalidate_filter()

    @Gtk.Template.Callback()
    def on_flowbox_child_activated(self, flowbox, child):
        self.confman.emit(
            'hydrapaper_flowbox_wallpaper_selected',
            child.wallpaper_path
        )
