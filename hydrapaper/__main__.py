from gettext import gettext as _
import sys
import argparse
from gi.repository import Gtk, Gio, GLib
from hydrapaper.confManager import ConfManager
from hydrapaper.app_window import HydraPaperAppWindow
from hydrapaper.get_gnome_dark_mode import get_gnome_dark_mode
from hydrapaper.preferences_window import PreferencesWindow
from hydrapaper.is_image import is_image
from hydrapaper.monitor_parser import build_monitors_autodetect
from hydrapaper.apply_wallpapers import apply_wallpapers
from hydrapaper.base_app import BaseApp, AppAction


class HydraPaperApplication(BaseApp):
    def __init__(self, **kwargs):
        self.confman = ConfManager()
        super().__init__(
            app_id='org.gabmus.hydrapaper',
            app_name='HydraPaper',
            app_actions=[
                AppAction(
                    name='spanned_mode',
                    func=self.toggle_spanned_mode,
                    accel=None,
                    stateful=True,
                    state_type=AppAction.StateType.BOOL,
                    state_default=self.confman.conf['spanned_mode']
                ),
                AppAction(
                    name='set_random_wallpaper',
                    func=lambda *args: self.apply_random(),
                    accel='<Primary><Shift>r'
                ),
                AppAction(
                    name='settings',
                    func=self.show_preferences_window,
                    accel='<Primary>comma'
                ),
                AppAction(
                    name='shortcuts',
                    func=self.show_shortcuts_window,
                    accel='<Primary>question'
                ),
                AppAction(
                    name='about',
                    func=self.show_about_dialog
                ),
                AppAction(
                    name='quit',
                    func=self.on_destroy_window,
                    accel='<Primary>q'
                ),
                AppAction(
                    name='search',
                    func=self.toggle_search,
                    accel='<Primary>f'
                )
            ],
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            css_resource='/org/gabmus/hydrapaper/ui/gtk_style.css'
        )

    def toggle_search(self, *args):
        self.window.headerbar.search_toggle.set_active(
            not self.window.headerbar.search_toggle.get_active()
        )

    def show_about_dialog(self, *args):
        about_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/aboutdialog.ui'
        )
        dialog = about_builder.get_object('aboutdialog')
        dialog.set_modal(True)
        dialog.set_transient_for(self.window)
        dialog.present()

    def on_destroy_window(self, *args):
        self.window.on_destroy()
        self.quit()

    def show_shortcuts_window(self, *args):
        shortcuts_win = Gtk.Builder.new_from_resource(
            '/org/gabmus/hydrapaper/ui/shortcutsWindow.ui'
        ).get_object('shortcuts-hydrapaper')
        shortcuts_win.props.section_name = 'shortcuts'
        shortcuts_win.set_transient_for(self.window)
        # shortcuts_win.set_attached_to(self.window)
        shortcuts_win.set_modal(True)
        shortcuts_win.present()
        shortcuts_win.show()

    def show_preferences_window(self, *args):
        preferences_win = PreferencesWindow(self.window)
        preferences_win.present()

    def apply_random(self):
        from random import randint
        monitors = build_monitors_autodetect()
        all_wallpapers = self.confman.wallpapers
        wallpapers = [
            all_wallpapers[
                randint(0, len(all_wallpapers)-1)
            ] for i in range(len(monitors))
        ]
        self.apply_from_cli(wallpapers)

    def apply_from_cli(self, wlist_cli, modes=None):
        # check all the passed wallpapers to be correct
        monitors = build_monitors_autodetect()
        if len(wlist_cli) < len(monitors):
            print(
                _('Error: you passed {0} wallpapers for {1} monitors').format(
                    len(wlist_cli), len(monitors)
                )
            )
            exit(1)
        if modes is None:
            modes = ['zoom' for i in range(len(monitors))]
        elif len(modes) < len(wlist_cli):
            print(
                _('Error: you passed {0} modes for {1} wallpapers').format(
                    len(modes), len(wlist_cli)
                )
            )
            exit(1)
        for monitor, mode in zip(monitors, modes):
            if mode not in ('zoom', 'fit_black', 'fit_blur',
                            'center_black', 'center_blur'):
                print(
                    _('Error: wallpaper mode {0} is not valid. '
                      'Allowed values are: zoom, fit_black, fit_blur, '
                      'center_black, center_blur').format(
                       mode
                    )
                )
                exit(1)
            monitor.mode = mode
        for wpath in wlist_cli:
            if not is_image(wpath):
                print(_('Error: {0} is not a valid image path').format(wpath))
                exit(1)
        for monitor, n_wp in zip(monitors, wlist_cli):
            monitor.wallpaper = n_wp
        n_monitors = {}
        for m in monitors:
            n_monitors[m.name] = m.wallpaper
        self.confman.conf['monitors'] = n_monitors
        self.confman.save_conf()
        print('>'*20)
        apply_wallpapers(monitors)

    def do_activate(self):
        super().do_activate()
        self.window = HydraPaperAppWindow()
        self.window.connect('close-request', self.on_destroy_window)
        self.add_window(self.window)
        if self.args:
            if self.args.wallpaper_path:
                self.apply_from_cli(
                    self.args.wallpaper_path[0],
                    self.args.wallpaper_modes[0]
                    if self.args.wallpaper_modes
                    else None,
                )
                self.quit()
                exit(0)
            if self.args.set_random:
                self.apply_random()
                self.quit()
                exit(0)
        self.window.present()
        self.window.show()

    def toggle_spanned_mode(self, action: Gio.SimpleAction, *args):
        action.change_state(
            GLib.Variant.new_boolean(not action.get_state().get_boolean())
        )
        self.confman.conf['spanned_mode'] = action.get_state().get_boolean()
        self.confman.emit('hydrapaper_spanned_mode_changed', '')

    def do_command_line(self, args):
        """
        GTK.Application command line handler
        called if Gio.ApplicationFlags.HANDLES_COMMAND_LINE is set.
        must call the self.do_activate() to get the application up and running.
        """
        # call the default commandline handler
        Gtk.Application.do_command_line(self, args)
        # make a command line parser
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-c', '--cli',
            dest='wallpaper_path',
            nargs='+', action='append',
            help=_('set wallpapers from command line')
        )
        parser.add_argument(
            '-m', '--modes',
            dest='wallpaper_modes',
            nargs='+', action='append',
            help=_('specify the modes for the wallpapers (zoom, center_black, '
                   'center_blur, fit_black, fit_blur)')
        )
        parser.add_argument(
            '-r', '--random',
            dest='set_random',
            action='store_true',
            help=_('set wallpapers randomly')
        )
        # parse the command line stored in args,
        # but skip the first element (the filename)
        self.args = parser.parse_args(args.get_arguments()[1:])
        # call the main program do_activate() to start up the app
        self.do_activate()
        return 0


def main():
    application = HydraPaperApplication()

    try:
        ret = application.run(sys.argv)
    except SystemExit as e:
        ret = e.code

    sys.exit(ret)


if __name__ == '__main__':
    main()
