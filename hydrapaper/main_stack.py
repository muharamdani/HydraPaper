from gettext import gettext as _
from gi.repository import Adw
from hydrapaper.wallpapers_flowbox import HydraPaperWallpapersFlowbox
from hydrapaper.search_bar import HpSearchBar


class HydraPaperMainStack(Adw.Bin):
    def __init__(self, searchbar: HpSearchBar):
        super().__init__(vexpand=True, hexpand=True)
        self.stack = Adw.ViewStack(vexpand=True, hexpand=True)
        self.set_child(self.stack)

        self.main_flowbox = HydraPaperWallpapersFlowbox(searchbar)
        self.favs_flowbox = HydraPaperWallpapersFlowbox(
            searchbar, is_favorites=True
        )

        self.stack.add_titled(
            self.main_flowbox, 'Wallpapers', _('Wallpapers')
        ).set_icon_name(
            'preferences-desktop-wallpaper-symbolic'
        )
        self.stack.add_titled(
            self.favs_flowbox, 'Favorites', _('Favorites')
        ).set_icon_name(
            'emblem-favorite-symbolic'
        )
