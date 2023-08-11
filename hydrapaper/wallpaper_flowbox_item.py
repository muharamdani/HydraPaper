from gettext import gettext as _
from gi.repository import Gtk, GLib
import os
from PIL import Image
from hashlib import sha256
from hydrapaper.confManager import ConfManager
from pathlib import Path
from threading import Thread


@Gtk.Template(
    resource_path='/org/gabmus/hydrapaper/ui/wallpaper_flowbox_item_popover.ui'
)
class WallpaperItemPopover(Gtk.Popover):
    __gtype_name__ = 'WallpaperFlowboxItemPopover'
    favorite_btn = Gtk.Template.Child()
    wallpaper_path_entry = Gtk.Template.Child()
    wallpaper_name_label = Gtk.Template.Child()

    def __init__(self, wp_path, parent_w, **kwargs):
        super().__init__(**kwargs)
        self.wp_path = wp_path
        self.parent_w = parent_w
        self.set_parent(self.parent_w)

    def popup(self, *args):
        if (
                self.parent_w.get_parent().get_parent().get_parent(
                    ).is_favorites or
                self.parent_w.is_fav
        ):
            self.favorite_btn.set_label(_('Remove favorite'))
        else:
            self.favorite_btn.set_label(_('Add favorite'))
        self.wallpaper_path_entry.set_text(self.wp_path)
        self.wallpaper_name_label.set_text(Path(self.wp_path).name)
        super().popup(*args)

    @Gtk.Template.Callback()
    def on_favorite_btn_clicked(self, btn):
        self.parent_w.set_fav(not self.parent_w.is_fav)
        self.parent_w.confman.emit('hydrapaper_populate_wallpapers', '')
        self.popdown()


@Gtk.Template(
    resource_path='/org/gabmus/hydrapaper/ui/wallpaper_flowbox_item.ui'
)
class WallpaperBox(Gtk.FlowBoxChild):
    __gtype_name__ = 'WallpaperBox'
    wp_image = Gtk.Template.Child()
    heart_icon = Gtk.Template.Child()
    container_box = Gtk.Template.Child()
    label = Gtk.Template.Child()

    def __init__(self, wp_path, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.wallpaper_path = wp_path
        self.popover = WallpaperItemPopover(self.wallpaper_path, self)
        self.pathlib_path = Path(wp_path)
        self.cache_path = '{0}/{1}.png'.format(
            self.confman.thumbs_cache_path,
            sha256(
                f'HydraPaperThumb{self.wallpaper_path}'.encode()
            ).hexdigest()
        )
        self.is_fav = False
        self.container_box.wallpaper_path = wp_path
        self.resolution = ''

        self.set_wallpaper_thumb()
        self.set_fav(self.wallpaper_path in self.confman.conf['favorites'])

        self.click_gesture = Gtk.GestureClick.new()
        self.click_gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.click_gesture.set_button(3)
        self.click_gesture.connect(
            'released', self.on_rightclick
        )
        self.add_controller(self.click_gesture)

        self.longpress = Gtk.GestureLongPress.new()
        self.longpress.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        self.longpress.set_touch_only(False)
        self.longpress.connect(
            'pressed',
            self.on_rightclick
        )
        self.add_controller(self.longpress)
        self.label.set_text(self.pathlib_path.stem)

    def on_rightclick(self, *args):
        self.get_parent().select_child(self)
        self.confman.emit(
            'hydrapaper_flowbox_wallpaper_selected',
            self.wallpaper_path
        )
        self.popover.popup()

    def set_size_tooltip(self):
        with Image.open(self.wallpaper_path) as img:
            self.resolution = 'x'.join([
                str(dim) for dim in img.size
            ])
            GLib.idle_add(
                lambda: self.wp_image.set_tooltip_text(self.resolution)
            )

    def set_wallpaper_thumb(self):

        def af():
            self.make_wallpaper_thumb(self.cache_path)
            GLib.idle_add(cb)

        def cb():
            self.wp_image.set_filename(self.cache_path)
            self.wp_image.show()

        if os.path.isfile(self.cache_path):
            cb()
            Thread(target=self.set_size_tooltip(), daemon=True).start()
        else:
            Thread(target=af, daemon=True).start()

    def set_fav(self, fav: bool):
        self.is_fav = fav
        if self.is_fav:
            self.heart_icon.set_visible(True)
            if self.wallpaper_path not in self.confman.conf['favorites']:
                self.confman.conf['favorites'].append(self.wallpaper_path)
        else:
            self.heart_icon.set_visible(False)
            if self.wallpaper_path in self.confman.conf['favorites']:
                self.confman.conf['favorites'].pop(
                    self.confman.conf['favorites'].index(self.wallpaper_path)
                )
        self.confman.save_conf()

    def make_wallpaper_thumb(self, wp_path):
        try:
            thumb = Image.open(self.wallpaper_path)
            self.resolution = 'x'.join([
                str(dim) for dim in thumb.size
            ])
            GLib.idle_add(
                lambda: self.wp_image.set_tooltip_text(self.resolution)
            )
            thumb.thumbnail((250, 250), Image.ANTIALIAS)
            thumb.save(self.cache_path, 'PNG')
            thumb.close()
        except IOError:
            print(
                _('ERROR: cannot create thumbnail for file'),
                self.wallpaper_path
            )
        return self.cache_path
