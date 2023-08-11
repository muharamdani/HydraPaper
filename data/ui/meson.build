LIBEXEC_DIR = join_paths(get_option('prefix'), get_option('libexecdir'))
EXTENSION_DIR = join_paths(get_option('prefix'), get_option('libdir'), meson.project_name())

ui_conf = configuration_data()
ui_conf.set('PACKAGE_URL', website)
ui_conf.set('DATA_DIR', pkgdatadir)
ui_conf.set('EXTENSION_DIR', EXTENSION_DIR)
ui_conf.set('LOCALE_DIR', join_paths(get_option('prefix'), get_option('datadir'), 'locale'))
ui_conf.set('APPID', app_id)
ui_conf.set('libexecdir', LIBEXEC_DIR)
# this is for development version # ui_conf.set('VERSION', ''.join([run_command(['git', 'describe', '--long', '--tags']).stdout(), get_option('profile')]))
ui_conf.set('VERSION', meson.project_version())
ui_conf.set('CONTRIBUTORS', contributors)
ui_conf.set('TRANSLATORS', translators)
ui_conf.set('DESIGNERS', designers)
ui_conf.set('authorfullname', authorfullname)
ui_conf.set('prettyname', prettyname)

# this has been moved to /data/meson.build
#configure_file(
#    input: 'aboutdialog.ui.in',
#    output: 'aboutdialog.ui',
#    configuration: ui_conf
#)
