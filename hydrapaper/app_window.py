from gi.repository import Gtk, Adw
from hydrapaper.confManager import ConfManager
from hydrapaper.main_stack import HydraPaperMainStack
from hydrapaper.monitors_flowbox import HydraPaperMonitorsFlowbox
from hydrapaper.apply_wallpapers import apply_wallpapers
from hydrapaper.headerbar import HydraPaperHeaderbar
from hydrapaper.base_app import BaseWindow, AppShortcut
from hydrapaper.search_bar import HpSearchBar


class HydraPaperAppWindow(BaseWindow):
    def __init__(self):
        super().__init__(
            app_name='HydraPaper',
            icon_name='org.gabmus.hydrapaper',
            shortcuts=[AppShortcut(
                'F10', lambda *args: self.headerbar.menu_button.popup()
            )]
        )
        self.confman = ConfManager()

        self.content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, hexpand=True, vexpand=True
        )

        self.folders_flap = Adw.Flap(
            flap_position=Gtk.PackType.START,
            fold_policy=Adw.FlapFoldPolicy.ALWAYS,
            modal=True,
            reveal_flap=False,
            swipe_to_open=True, swipe_to_close=True
        )
        self.folders_flap.set_content(self.content_box)

        self.bottom_bar = Adw.ViewSwitcherBar()
        self.headerbar = HydraPaperHeaderbar(
            self, self.apply_handler, self.folders_flap
        )

        self.searchbar = HpSearchBar(self.headerbar.search_toggle)
        self.main_stack = HydraPaperMainStack(self.searchbar)

        self.stack_switcher = self.headerbar.stack_switcher
        self.folders_view = self.headerbar.folders_view
        self.stack_switcher.set_stack(self.main_stack.stack)
        self.bottom_bar.set_stack(self.main_stack.stack)
        self.monitors_flowbox = HydraPaperMonitorsFlowbox()

        self.append(self.headerbar)
        self.append(self.searchbar)
        self.content_box.append(self.monitors_flowbox)
        self.content_box.append(self.main_stack)
        self.content_box.append(self.bottom_bar)
        self.append(self.folders_flap)

        self.confman.connect(
            'dark_mode_changed',
            lambda *args: self.set_dark_mode(self.confman.conf['dark_mode'])
        )
        self.set_dark_mode(self.confman.conf['dark_mode'])

    def present(self):
        super().present()
        self.set_default_size(
            self.confman.conf['windowsize']['width'],
            self.confman.conf['windowsize']['height']
        )

    def emit_destroy(self, *args):
        self.emit('destroy')

    def show(self, **kwargs):
        super().show(**kwargs)
        self.main_stack.main_flowbox.show_hide_wallpapers()

    def apply_handler(self, _, set_dark=False):
        apply_wallpapers(
            monitors=self.monitors_flowbox.get_monitors(),
            widgets_to_freeze=[
                self.headerbar.apply_btn,
                self.headerbar.apply_dark_btn,
                self.folders_view
            ],
            set_dark=set_dark
        )
        self.monitors_flowbox.dump_to_config()

    def on_destroy(self, *args):
        self.confman.conf['windowsize'] = {
            'width': self.get_width(),
            'height': self.get_height()
        }
        self.confman.save_conf()
