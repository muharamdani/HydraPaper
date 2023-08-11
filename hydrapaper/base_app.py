from gi.repository import Adw, Gtk, GLib, Gio, Gdk
from typing import Callable, Optional, List, Any
from enum import Enum, auto


class AppAction:
    class StateType(Enum):
        BOOL = auto()
        RADIO = auto()

    def __init__(
            self,
            name: str,
            func: Callable,
            accel: Optional[str] = None,
            stateful: bool = False,
            state_type: Optional[StateType] = None,
            state_default: Any = None
    ):
        self.name = name
        self.func = func
        self.accel = accel
        self.stateful = stateful
        self.state_type = state_type
        self.state_default = state_default

        assert(not self.stateful or self.state_default is not None)

    def get_action(self):
        action = None
        if self.stateful:
            parameter_type = None
            variant = None
            if self.state_type == AppAction.StateType.BOOL:
                variant = GLib.Variant.new_boolean(self.state_default)
            elif self.state_type == AppAction.StateType.RADIO:
                parameter_type = GLib.VariantType.new('s')
                variant = GLib.Variant('s', self.state_default)
            action = Gio.SimpleAction.new_stateful(
                self.name, parameter_type, variant
            )
        else:
            action = Gio.SimpleAction.new(self.name, None)
        action.connect('activate', self.func)
        return action


class BaseApp(Gtk.Application):
    def __init__(
            self,
            app_id: str,
            app_name: str,
            app_actions: List[AppAction] = [],
            flags: int = 0,
            css_resource: Optional[str] = None
    ):
        self.app_actions = app_actions
        self.css_resource = css_resource
        super().__init__(application_id=app_id, flags=flags)
        GLib.set_application_name(app_name)
        GLib.set_prgname(app_id)

    def do_startup(self):
        Gtk.Application.do_startup(self)
        Adw.init()
        for a in self.app_actions:
            action = a.get_action()
            self.add_action(action)
            if a.accel is not None:
                self.set_accels_for_action(f'app.{a.name}', [a.accel])

    def load_css(self):
        if self.css_resource is None:
            return
        provider = Gtk.CssProvider()
        provider.load_from_resource(self.css_resource)
        display = Gdk.Display.get_default()
        if display is not None:
            Gtk.StyleContext.add_provider_for_display(
                display, provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def do_activate(self):
        self.load_css()


class AppShortcut:
    def __init__(self, keystroke: str, callback: Callable):
        self.keystroke = keystroke
        self.callback = callback

    def bind(self, widget: Gtk.Widget):
        assert hasattr(widget, '_shortcut_controller')
        _, key, mod = Gtk.accelerator_parse(self.keystroke)
        trigger = Gtk.KeyvalTrigger.new(key, mod)
        cb = Gtk.CallbackAction.new(self.callback)
        shortcut = Gtk.Shortcut.new(trigger, cb)
        widget._shortcut_controller.add_shortcut(shortcut)

    @classmethod
    def create_controller(cls, widget: Gtk.Widget):
        widget._shortcut_controller = Gtk.ShortcutController()
        widget._shortcut_controller.set_scope(Gtk.ShortcutScope.GLOBAL)
        widget.add_controller(widget._shortcut_controller)


class BaseWindow(Adw.ApplicationWindow):
    def __init__(
            self,
            app_name: str,
            icon_name: str,
            shortcuts: List[AppShortcut] = []
    ):
        super().__init__()
        self.set_title(app_name)
        self.set_icon_name(icon_name)
        AppShortcut.create_controller(self)
        for shortcut in shortcuts:
            shortcut.bind(self)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)

        self.append = self.main_box.append
        self.prepend = self.main_box.prepend
        self.remove = self.main_box.remove

    def set_dark_mode(self, dark_mode: bool = False):
        Adw.StyleManager.get_default().set_color_scheme(
            Adw.ColorScheme.FORCE_DARK if dark_mode
            else Adw.ColorScheme.DEFAULT
        )
