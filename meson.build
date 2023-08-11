project('hydrapaper',
    version: '3.3.1',
    meson_version: '>= 0.58.0',
    license: 'GPL3'
)

description = 'Wallpaper manager with multimonitor support'
prettyname = 'HydraPaper'
prettylicense = 'GPL-3.0+'

author = 'gabmus'
authorfullname = 'Gabriele Musco'
authoremail = 'gabmus@disroot.org'
domain = 'org'
# app_id built as: domain.author.project_name
gitrepo = 'https://gitlab.com/'+author+'/'+meson.project_name()
website = 'http://'+meson.project_name()+'.'+author+'.org'

# NOTE: if you contributed, feel free to add your name and email address here
contributors = '\n'.join([
    'Gabriele Musco (GabMus) &lt;gabmus@disroot.org&gt;',
    'Alex Hunt (huntie) &lt;hello@alexhunt.io&gt;'
])

translators = '\n'.join([
    'German: Alessandra Gallia &lt;alessandragalliaaru@gmail.com&gt;',
    'Russian: Alessandra Gallia &lt;alessandragalliaaru@gmail.com&gt;',
    'Italian: Gabriele Musco (GabMus) &lt;gabmus@disroot.org&gt;',
    'Swedish: Åke Engelbrektson &lt;eson@svenskasprakfiler.se&gt;'
])

designers = '\n'.join([
    'Icon by Tobias Bernard (bertob) &lt;hi@tobiasbernard.com&gt;'
])

message('Looking for dependencies')
dependency('glib-2.0')
dependency('gobject-introspection-1.0', version: '>=1.35.9')
dependency('gtk4', version :'>=4.3.1')
dependency('libadwaita-1', version :'>=1.0.0.alpha.3')

i18n = import('i18n')
python = import('python')
py_installation = python.find_installation('python3')
if not py_installation.found()
    error('No valid python3 binary found')
endif
gnome = import('gnome')
prefix = get_option('prefix') # should be /usr
bindir = get_option('bindir') # should be bin
datadir = get_option('datadir') # should be /usr/share
pkgdatadir = join_paths(prefix, datadir, meson.project_name())
# pythondir = join_paths(prefix, python.sysconfig_path('purelib'))
pythondir = py_installation.get_install_dir()
localedir = join_paths(prefix, get_option('localedir'))
libexecdir = join_paths(prefix, get_option('libexecdir'))
etcdir = get_option('sysconfdir')
systemd_user_unit_dir = join_paths(prefix, 'lib', 'systemd', 'user')
dependency('dbus-1')
dbus_service_dir = join_paths(datadir, 'dbus-1/services')
# dbus_service_dir = dependency(
#     'dbus-1'
# ).get_variable(
#     pkgconfig: 'session_bus_services_dir',
#     default_value: ['datadir', join_paths(prefix, datadir)]
# )

app_id = '.'.join([
    domain,
    author,
    meson.project_name()
])
app_id_aspath = '/'.join([
    domain,
    author,
    meson.project_name()
])

install_subdir(meson.project_name(), install_dir: pythondir)
subdir('data')
subdir('bin')
subdir('po')
subdir('docs')


meson.add_install_script('meson_post_install.py')
