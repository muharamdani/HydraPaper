from gi.repository import Gtk
from hydrapaper.get_desktop_environment import get_desktop_environment
from hydrapaper.wallpapers_folders_view import HydraPaperWallpapersFoldersView
from hydrapaper.confManager import ConfManager
from hydrapaper.slideshow_listbox_row import SlideshowListboxRow


@Gtk.Template(resource_path='/org/gabmus/hydrapaper/ui/headerbar.ui')
class HydraPaperHeaderbar(Gtk.WindowHandle):
    __gtype_name__ = 'GHeaderbar'
    headerbar = Gtk.Template.Child()
    stack_switcher = Gtk.Template.Child()
    squeezer = Gtk.Template.Child()
    nobox = Gtk.Template.Child()
    apply_btn = Gtk.Template.Child()
    menu_btn = Gtk.Template.Child()
    wallpaper_folders_btn = Gtk.Template.Child()
    add_to_slideshow_btn = Gtk.Template.Child()
    slideshow_menu_btn = Gtk.Template.Child()
    slideshow_switch = Gtk.Template.Child()
    slideshow_time_spinbutton = Gtk.Template.Child()
    slideshow_listbox = Gtk.Template.Child()
    search_toggle = Gtk.Template.Child()
    apply_dark_btn = Gtk.Template.Child()

    def __init__(self, window, apply_handler, folders_flap):
        super().__init__()
        self.confman = ConfManager()
        self.pack_start = self.headerbar.pack_start
        self.pack_end = self.headerbar.pack_end
        self.set_title_widget = self.headerbar.set_title_widget
        self.apply_handler_func = apply_handler
        self.folders_flap = folders_flap
        self.bottom_bar = window.bottom_bar

        self.folders_view = HydraPaperWallpapersFoldersView(window)
        self.folders_flap.set_flap(self.folders_view)
        self.folders_flap.connect(
            'notify::reveal-flap', lambda *args:
                self.wallpaper_folders_btn.set_active(
                    self.folders_flap.get_reveal_flap()
                )
        )

        if True:  # TODO: rework background worker
            self.slideshow_menu_btn.set_visible(False)
        self.slideshow_switch.set_state(
            self.confman.conf['Daemon']['wallpaper_rotation_enabled']
        )
        self.slideshow_time_spinbutton.set_increments(1, 10)
        self.slideshow_time_spinbutton.set_range(0, 300000)
        self.slideshow_time_spinbutton.set_value(
            self.confman.conf['Daemon']['wallpaper_rotation_sleep_time']
        )
        self.slideshow_listbox.populate = self.populate_slideshow_listbox
        self.on_slideshow_mode_changed()
        self.populate_slideshow_listbox()

        self.apply_dark_btn.set_visible(
            'gnome' in get_desktop_environment() or
            'ubuntu' in get_desktop_environment()
        )

    def signal_daemon(self):
        if True:  # TODO: rework background worker
            return

    @Gtk.Template.Callback()
    def on_slideshow_time_spinbutton_changed(self, *args):
        self.confman.conf['Daemon']['wallpaper_rotation_sleep_time'] = \
            self.slideshow_time_spinbutton.get_value()
        self.confman.save_conf()
        self.signal_daemon()

    @Gtk.Template.Callback()
    def on_add_to_slideshow(self, *args):
        monitors = self.get_root().monitors_flowbox.get_monitors()
        pics = [{
            'wallpaper': m.wallpaper, 'mode': m.mode,
            'single_spanned': self.confman.conf['spanned_mode']
        } for m in monitors]
        # pics = [m.wallpaper for m in monitors]
        if None in pics:
            return
        self.confman.conf['Daemon']['rotating_wallpapers'].append(pics)
        self.confman.save_conf()
        self.signal_daemon()
        self.populate_slideshow_listbox()

    def populate_slideshow_listbox(self, *args):
        child = self.slideshow_listbox.get_first_child()
        while child is not None:
            self.slideshow_listbox.remove(child)
            child = self.slideshow_listbox.get_first_child()
        for pics in self.confman.conf['Daemon']['rotating_wallpapers']:
            self.slideshow_listbox.append(
                SlideshowListboxRow([pic['wallpaper'] for pic in pics])
            )
        self.signal_daemon()

    @Gtk.Template.Callback()
    def on_slideshow_mode_changed(self, *args):
        n_state = self.slideshow_switch.get_active()
        if True:  # TODO: rework background worker
            n_state = False
        self.confman.conf['Daemon']['wallpaper_rotation_enabled'] = n_state
        self.confman.save_conf_async()
        sc = self.slideshow_menu_btn.get_style_context()
        for c in [f'slideshow-btn-{p}active' for p in ('', 'in')]:
            sc.remove_class(c)
        if n_state:
            sc.add_class('slideshow-btn-active')
            self.add_to_slideshow_btn.set_visible(True)
            self.apply_btn.set_visible(False)
        else:
            sc.add_class('slideshow-btn-inactive')
            self.add_to_slideshow_btn.set_visible(False)
            self.apply_btn.set_visible(True)
        self.signal_daemon()

    @Gtk.Template.Callback()
    def on_squeeze(self, *args):
        self.bottom_bar.set_reveal(
            self.squeezer.get_visible_child() == self.nobox
        )

    def apply_handler(self, *args, **kwargs):
        self.apply_handler_func(*args, **kwargs)
        self.confman.save_conf()
        self.signal_daemon()

    @Gtk.Template.Callback()
    def on_apply_btn_clicked(self, btn):
        self.apply_handler(self.apply_dark_btn)

    @Gtk.Template.Callback()
    def on_apply_dark_btn_clicked(self, btn):
        self.apply_handler(self.apply_btn, set_dark=True)

    @Gtk.Template.Callback()
    def on_wallpaper_folders_btn_clicked(self, *args):
        self.folders_flap.set_reveal_flap(
            self.wallpaper_folders_btn.get_active()
        )
