from gettext import gettext as _
from gi.repository import Gtk, Adw, Gio, GObject
from hydrapaper.confManager import ConfManager
from typing import Optional, Union, List, Callable


class MActionRow(Adw.ActionRow):
    def __init__(self, title: str, subtitle: Optional[str] = None, **kwargs):
        self.title = title
        self.subtitle = subtitle
        super().__init__(
            title=self.title,
            title_lines=0, subtitle_lines=0,
            **kwargs
        )
        if self.subtitle:
            self.set_subtitle(self.subtitle)


class PreferencesButtonRow(MActionRow):
    """
    A preferences row with a title and a button
    title: the title shown
    button_label: a label to show inside the button
    onclick: the function that will be called when the button is pressed
    subtitle: an optional subtitle to be shown
    button_style_class: the style class of the button.
        Common options: `suggested-action`, `destructive-action`
    signal: an optional signal to let ConfManager emit when the button is
        pressed
    """
    def __init__(
            self, title: str, button_label: str,
            onclick: Callable, subtitle: Optional[str] = None,
            button_style_class: Optional[str] = None,
            signal: Optional[str] = None
    ):
        super().__init__(title, subtitle)
        self.button_label = button_label
        self.confman = ConfManager()
        self.signal = signal
        self.onclick = onclick

        self.button = Gtk.Button(
            label=self.button_label, valign=Gtk.Align.CENTER
        )
        if button_style_class:
            self.button.get_style_context().add_class(button_style_class)
        self.button.connect('clicked', self.on_button_clicked)
        self.add_suffix(self.button)

    def on_button_clicked(self, btn):
        self.onclick(self.confman)
        if self.signal:
            self.confman.emit(self.signal, '')
        self.confman.save_conf()


class PreferencesEntryRow(MActionRow):
    """
    A preferences row with a title and a button
    title: the title shown
    conf_key: the key of the configuration dictionary/json in ConfManager
    subtitle: an optional subtitle to be shown
    onchange: an optional function that will be called when the entry changes
    signal: an optional signal to let ConfManager emit when the entry changes
    """
    def __init__(
            self, title: str, conf_key: str, subtitle: Optional[str] = None,
            onchange: Optional[Callable] = None, signal: Optional[str] = None
    ):
        super().__init__(title, subtitle)
        self.conf_key = conf_key
        self.confman = ConfManager()
        self.signal = signal
        self.onchange = onchange

        self.entry = Gtk.Entry(valign=Gtk.Align.CENTER)
        self.entry.set_text(self.confman.conf[self.conf_key])
        self.entry.connect('changed', self.on_entry_changed)
        self.add_suffix(self.entry)

    def on_entry_changed(self, *args):
        self.confman.conf[self.conf_key] = self.entry.get_text().strip()
        if self.onchange is not None:
            self.onchange(self.confman)
        if self.signal:
            self.confman.emit(self.signal, '')
        self.confman.save_conf()


class PreferencesFileChooserRow(MActionRow):
    """
    A preferences row with a title and a file chooser button
    title: the title shown
    conf_key: the key of the configuration dictionary/json in ConfManager
    subtitle: an optional subtitle to be shown
    signal: an optional signal to let ConfManager emit when the value changes
    file_chooser_title: the title of the file chooser dialog
    file_chooser_action: the title of the file chooser dialog
    """

    def __init__(
            self, title: str, conf_key: str, subtitle: Optional[str] = None,
            signal: Optional[str] = None,
            file_chooser_title: str = _('Choose a folder'),
            file_chooser_action: Gtk.FileChooserAction =
            Gtk.FileChooserAction.SELECT_FOLDER
    ):
        super().__init__(title, subtitle)
        self.confman = ConfManager()
        self.signal = signal
        self.conf_key = conf_key

        self.file_chooser_btn = Gtk.FileChooserButton.new(
            file_chooser_title, file_chooser_action
        )
        self.file_chooser_btn.set_current_folder_uri(
            'file://'+self.confman.conf[self.conf_key]
        )

        self.file_chooser_btn.connect('file-set', self.on_file_set)
        self.add(self.file_chooser_btn)

    def on_file_set(self, *args):
        self.confman.conf[self.conf_key] = self.file_chooser_btn.get_filename()
        if self.signal:
            self.confman.emit(self.signal, '')
        self.confman.save_conf()


class PreferencesSpinButtonRow(MActionRow):
    """
    A preferences row with a title and a spin button
    title: the title shown
    min_v: minimum num value
    max_v: maximum num value
    conf_key: the key of the configuration dictionary/json in ConfManager
    subtitle: an optional subtitle to be shown
    signal: an optional signal to let ConfManager emit when the value changes
    """

    def __init__(
            self, title: str, min_v: int, max_v: int, conf_key: str,
            subtitle: Optional[str] = None, signal: Optional[str] = None
    ):
        super().__init__(title, subtitle)
        self.confman = ConfManager()
        self.signal = signal
        self.conf_key = conf_key

        self.adjustment = Gtk.Adjustment.new(
            self.confman.conf[self.conf_key],  # initial value
            min_v,  # minimum value
            max_v,  # maximum value
            1,  # step increment
            10,  # page increment (page up, page down? large steps anyway)
            0
        )

        self.spin_button = Gtk.SpinButton(
            adjustment=self.adjustment, valign=Gtk.Align.CENTER
        )
        self.spin_button.connect('value-changed', self.on_value_changed)
        self.add_suffix(self.spin_button)

    def on_value_changed(self, *args):
        self.confman.conf[self.conf_key] = self.spin_button.get_value_as_int()
        if self.signal:
            self.confman.emit(self.signal, self.confman.conf[self.conf_key])
        self.confman.save_conf()


class PreferencesComboRow(Adw.ComboRow):
    """
    A preferences row with a title and a combo box
    title: the title shown
    values: a list of acceptable values
    value_names: a list of user facing names for the values provided above
    conf_key: the key of the configuration dictionary/json in ConfManager
    subtitle: an optional subtitle to be shown
    signal: an optional signal to let ConfManager emit when the value changes
    """

    class ItemWrapper(GObject.Object):
        def __init__(self, name: str, value: str):
            super().__init__()
            self.name = name
            self.value = value

    def __init__(
            self, title: str, values: List[str], value_names: List[str],
            conf_key: str, subtitle: Optional[str] = None,
            signal: Optional[str] = None
    ):
        self.confman = ConfManager()
        self.signal = signal
        self.conf_key = conf_key
        self.list_store = Gio.ListStore(
            item_type=PreferencesComboRow.ItemWrapper
        )
        self.items_l = list()
        for name, value in zip(value_names, values):
            i = PreferencesComboRow.ItemWrapper(name, value)
            self.items_l.append(i)
            self.list_store.append(i)
        self.factory = Gtk.SignalListItemFactory()
        self.factory.connect('setup', self._on_setup_listitem)
        self.factory.connect('bind', self._on_bind_listitem)

        self.title = title
        self.subtitle = subtitle

        super().__init__(
            model=self.list_store, factory=self.factory, title=title
        )
        if self.subtitle:
            self.set_subtitle(self.subtitle)

        self.set_selected(values.index(self.confman.conf[self.conf_key]))

        self.connect('notify::selected-item', self.on_selection_changed)

    def _on_setup_listitem(
            self, factory: Gtk.ListItemFactory, list_item: Gtk.ListItem
    ):
        label = Gtk.Label()
        list_item.set_child(label)
        list_item.row_w = label

    def _on_bind_listitem(
            self, factory: Gtk.ListItemFactory, list_item: Gtk.ListItem
    ):
        label = list_item.get_child()
        label.set_text(list_item.get_item().name)

    def on_selection_changed(self, *args):
        value = self.get_selected_item().value
        if value is not None:
            self.confman.conf[self.conf_key] = value
            if self.signal:
                self.confman.emit(self.signal, '')
            self.confman.save_conf()


class PreferencesToggleRow(MActionRow):
    """
    A preferences row with a title and a toggle
    title: the title shown
    conf_key: the key of the configuration dictionary/json in ConfManager
    subtitle: an optional subtitle to be shown
    signal: an optional signal to let ConfManager emit when the configuration
        is set
    """
    def __init__(
            self, title: str, conf_key: str, subtitle: Optional[str] = None,
            signal: Optional[str] = None
    ):
        super().__init__(title, subtitle)
        self.confman = ConfManager()
        self.conf_key = conf_key
        self.signal = signal

        self.toggle = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.toggle.set_active(self.confman.conf.get(self.conf_key, False))
        self.toggle.connect('state-set', self.on_toggle_state_set)
        self.add_suffix(self.toggle)
        self.set_activatable_widget(self.toggle)

    def on_toggle_state_set(self, toggle, state):
        self.confman.conf[self.conf_key] = state
        self.confman.save_conf()
        if self.signal is not None:
            self.confman.emit(self.signal, '')


class MPreferencesGroup(Adw.PreferencesGroup):
    def __init__(
            self, title: str,
            rows: List[Union[MActionRow, PreferencesComboRow, Adw.ActionRow]]
    ):
        self.title = title
        self.rows = rows
        super().__init__(title=self.title)
        for row in self.rows:
            self.add(row)


class MPreferencesPage(Adw.PreferencesPage):
    def __init__(
            self, title: str, pref_groups: List[MPreferencesGroup],
            icon_name: Optional[str] = None
    ):
        self.title = title
        self.icon_name = icon_name
        self.pref_groups = pref_groups
        super().__init__(title=self.title)
        if self.icon_name:
            self.set_icon_name(self.icon_name)
        for group in self.pref_groups:
            self.add(group)
