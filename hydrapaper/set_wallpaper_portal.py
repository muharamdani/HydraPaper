import dbus


def set_wallpaper(path):
    bus = dbus.SessionBus()
    portal_desktop = bus.get_object(
        'org.freedesktop.portal.Desktop',
        '/org/freedesktop/portal/desktop'
    )
    interface_wp = dbus.Interface(
        portal_desktop,
        dbus_interface='org.freedesktop.portal.Wallpaper'
    )
    with open(path.replace('file://', ''), 'rb') as fd:
        interface_wp.SetWallpaperFile('', fd.fileno(), {
            'show-preview': False,
            'set-on': 'background'
        })
