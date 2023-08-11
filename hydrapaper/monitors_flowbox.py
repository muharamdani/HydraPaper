from gi.repository import Gtk, GdkPixbuf
from hydrapaper.confManager import ConfManager
from hydrapaper.monitor_parser import (
    build_monitors_autodetect,
    build_combined_spanned_monitor
)
from hydrapaper.is_image import is_image
from hashlib import sha256
from os.path import isfile


WALLPAPER_MODE_VALUES = [
    'zoom', 'fit_black', 'fit_blur', 'center_black', 'center_blur'
]


@Gtk.Template(
    resource_path='/org/gabmus/hydrapaper/ui/wp_mode_popover_menu.ui'
)
class WallpaperModePopoverContent(Gtk.ScrolledWindow):
    __gtype_name__ = 'WallpaperModePopoverContent'
    radio_zoom = Gtk.Template.Child()
    radio_fit_black = Gtk.Template.Child()
    radio_fit_blur = Gtk.Template.Child()
    radio_center_black = Gtk.Template.Child()
    radio_center_blur = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self.radios_dict = {
            'zoom': self.radio_zoom,
            'fit_black': self.radio_fit_black,
            'fit_blur': self.radio_fit_blur,
            'center_black': self.radio_center_black,
            'center_blur': self.radio_center_blur
        }
        self.radios = list(self.radios_dict.values())


class WallpaperModePopover(Gtk.PopoverMenu):
    def __init__(self):
        super().__init__(autohide=True)
        self.content = WallpaperModePopoverContent()
        self.radios_dict = self.content.radios_dict
        self.radios = self.content.radios
        self.set_child(self.content)


@Gtk.Template(
    resource_path='/org/gabmus/hydrapaper/ui/monitors_flowbox_item.ui'
)
class HydraPaperMonitorsFlowboxItem(Gtk.FlowBoxChild):
    __gtype_name__ = 'MonitorsFlowboxItem'
    main_box = Gtk.Template.Child()
    overlay = Gtk.Template.Child()
    image = Gtk.Template.Child()
    wp_mode_btn = Gtk.Template.Child()
    label = Gtk.Template.Child()

    def __init__(self, monitor, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.monitor = monitor

        self.label.set_text(self.monitor.name)
        self.wp_mode_popover = WallpaperModePopover()
        self.wp_mode_btn.set_popover(self.wp_mode_popover)

        for radio, value in zip(
                self.wp_mode_popover.radios,
                WALLPAPER_MODE_VALUES
        ):
            radio.connect(
                'toggled',
                self.on_wp_mode_changed,
                value
            )

        self.set_picture()

    def on_wp_mode_changed(self, radio, value):
        # check that the signal is sent from a radio that has been turned on
        # and not turned off by another radio
        if radio.get_active():
            self.monitor.mode = value

    def set_picture(self, n_wp=None):
        wp_size = 256 if self.confman.conf['big_monitor_thumbnails'] else 64
        self.image.set_pixel_size(wp_size)
        if n_wp and is_image(n_wp):
            self.monitor.wallpaper = n_wp
        if self.monitor.wallpaper and is_image(self.monitor.wallpaper):
            thumb_path = '{0}/{1}.png'.format(
                self.confman.thumbs_cache_path,
                sha256(
                    f'HydraPaperThumb{self.monitor.wallpaper}'.encode()
                ).hexdigest()
            )
            if not isfile(thumb_path):
                thumb_path = self.monitor.wallpaper
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                thumb_path, wp_size, wp_size, True
            )
            self.image.set_from_pixbuf(pixbuf)
        else:
            self.image.set_from_icon_name(
                'image-x-generic-symbolic'
            )
        self.wp_mode_popover.radios_dict[self.monitor.mode].set_active(True)


class HydraPaperMonitorsFlowbox(Gtk.FlowBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.monitors = build_monitors_autodetect()
        self.spanned_monitor = build_combined_spanned_monitor()

        self.set_min_children_per_line(1)
        self.set_max_children_per_line(len(self.monitors))
        self.set_halign(Gtk.Align.FILL)
        self.set_hexpand(True)
        self.set_homogeneous(False)
        self.set_vexpand(False)
        self.set_activate_on_single_click(True)
        self.confman.connect(
            'hydrapaper_flowbox_wallpaper_selected',
            self.change_selected_wp
        )
        self.confman.connect(
            'hydrapaper_reload_monitor_thumbs',
            self.reload_children_pictures
        )
        self.confman.connect(
            'hydrapaper_spanned_mode_changed',
            self.populate
        )
        self.populate()

    def populate(self, *args):
        while True:
            item = self.get_child_at_index(0)
            if item is not None:
                self.remove(item)
            else:
                break
        if self.confman.conf['spanned_mode']:
            self.insert(
                HydraPaperMonitorsFlowboxItem(
                    self.spanned_monitor
                ), -1
            )
            self.set_max_children_per_line(1)
        else:
            for m in self.monitors:
                self.insert(
                    HydraPaperMonitorsFlowboxItem(m), -1
                )
            self.set_max_children_per_line(len(self.monitors))
        self.select_child(self.get_child_at_index(0))

    def get_monitors(self):
        return (
            [self.spanned_monitor]
            if self.confman.conf['spanned_mode']
            else self.monitors
        )

    def reload_children_pictures(self, *args):
        i = 0
        child = self.get_child_at_index(i)
        while child is not None:
            child.set_picture()
            i += 1
            child = self.get_child_at_index(i)

    def dump_to_config(self):
        n_monitors = self.confman.conf['monitors'].copy()
        for m in self.monitors:
            n_monitors[m.name] = {
                'wallpaper': m.wallpaper,
                'mode': m.mode
            }
        self.confman.conf['monitors'] = n_monitors
        self.confman.save_conf()

    def change_selected_wp(self, signaler, n_wp, *args):
        selected_monitor_widget = self.get_selected_children()[0]
        if not selected_monitor_widget:
            return
        for i, m in enumerate(self.monitors):
            if m.name == selected_monitor_widget.monitor.name:
                self.monitors[i].wallpaper = n_wp
                break
        selected_monitor_widget.set_picture(n_wp)
